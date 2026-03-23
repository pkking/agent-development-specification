#!/usr/bin/env bash
# install.sh — 为目标 Go 项目安装 golang 项目模板规范
#
# 用法: ./install.sh <目标项目路径> [选项]
#
# 选项:
#   默认        git submodule（推荐）。规范以子模块形式引用，支持跨机器。
#   --copy      复制文件。适合 CI/CD 或无 git 场景，规范更新需重新运行。
#   --link      绝对路径符号链接。仅本机有效，不跨机器。
#   -y          非交互式，遇到冲突自动覆盖
#   --help      显示此帮助

set -euo pipefail

# ──────────────────────────── 常量 ────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 规范仓库 URL（用于 submodule 注册和 standalone 克隆）
SPEC_REPO_URL="https://github.com/opensourceways/agent-development-specification.git"

# 模板文件在仓库中的相对路径（相对于仓库根目录）
TEMPLATE_RULES_REL="spec/project-templates/golang/.claude/rules"
TEMPLATE_SETTINGS_REL="spec/project-templates/golang/.claude/settings.json"
TEMPLATE_CLAUDE_MD_REL="spec/project-templates/golang/CLAUDE.md"

# 检测运行模式：
#   in-repo   — 脚本在 agent-development-specification 仓库内部运行
#   standalone — 脚本被单独下载后独立运行
#
# 脚本位于 spec/project-templates/golang/，仓库根目录为 SCRIPT_DIR/../../..
_REPO_DIR="$(cd "${SCRIPT_DIR}/../../.." && pwd)"
if [[ -f "${_REPO_DIR}/${TEMPLATE_CLAUDE_MD_REL}" ]] \
    && [[ -d "${_REPO_DIR}/${TEMPLATE_RULES_REL}" ]]; then
    STANDALONE=false
    SPEC_REPO="$_REPO_DIR"
    RULES_SRC="${SPEC_REPO}/${TEMPLATE_RULES_REL}"
    SETTINGS_SRC="${SPEC_REPO}/${TEMPLATE_SETTINGS_REL}"
    CLAUDE_MD_SRC="${SPEC_REPO}/${TEMPLATE_CLAUDE_MD_REL}"
else
    STANDALONE=true
    SPEC_REPO=""
    RULES_SRC=""
    SETTINGS_SRC=""
    CLAUDE_MD_SRC=""
fi

# git submodule 相关路径（相对于目标项目根目录）
SUBMODULE_PATH=".claude/agent-development-specification"
# 相对符号链接：从 .claude/ 目录出发，指向子模块内的 rules 目录
RULES_LINK_TARGET="agent-development-specification/${TEMPLATE_RULES_REL}"

# CLAUDE.md 追加内容的标记，用于幂等检测
DEV_RULES_BEGIN="<!-- dev-rules:begin -->"
DEV_RULES_END="<!-- dev-rules:end -->"

# ──────────────────────────── 帮助 ────────────────────────────
usage() {
    cat <<EOF
用法: $(basename "$0") <目标项目路径> [选项]

在目标项目中安装 Go 项目开发规范：
  - .claude/agent-development-specification/  规范仓库子模块（submodule 模式）
  - .claude/rules/            规范文件目录（相对符号链接或副本）
  - .claude/settings.json     Claude Code 钩子配置
  - CLAUDE.md                 追加团队规范入口（已存在时追加，否则创建）

选项:
  默认      git submodule（推荐）
            将规范仓库以子模块方式引入，相对符号链接跨机器有效
  --copy    复制文件
            适合 CI/CD 或离线场景，规范更新需重新运行此脚本
  --link    绝对路径符号链接
            仅本机单人使用，不适合提交到 git
  -y        非交互式，遇到冲突自动覆盖
  --help    显示此帮助

示例:
  $(basename "$0") ~/workspace/my-service
  $(basename "$0") ~/workspace/my-service --copy
  $(basename "$0") ~/workspace/my-service -y

规范仓库: ${SPEC_REPO_URL}
EOF
}

# ──────────────────────────── 工具函数 ────────────────────────────
info()    { echo "[INFO]  $*"; }
warn()    { echo "[WARN]  $*" >&2; }
success() { echo "[OK]    $*"; }
error()   { echo "[ERROR] $*" >&2; exit 1; }

confirm_overwrite() {
    local description="$1"
    if [[ "$AUTO_YES" == true ]]; then return 0; fi
    read -r -p "  '${description}' 已存在，是否覆盖？[y/N] " reply
    [[ "$reply" =~ ^[Yy]$ ]]
}

# ──────────────────────────── 参数解析 ────────────────────────────
MODE="submodule"
TARGET=""
AUTO_YES=false

while [[ $# -gt 0 ]]; do
    case "$1" in
        --copy)      MODE="copy" ;;
        --link)      MODE="link" ;;
        -y|--yes)    AUTO_YES=true ;;
        --help|-h)   usage; exit 0 ;;
        -*)          error "未知选项: $1，使用 --help 查看用法" ;;
        *)
            [[ -n "$TARGET" ]] && error "多余的参数: $1"
            TARGET="$1"
            ;;
    esac
    shift
done

[[ -z "$TARGET" ]] && { usage; error "未指定目标项目路径"; }

# realpath -m 允许路径不存在时仍返回规范化路径
TARGET="$(realpath -m "$TARGET")"

# ──────────────────────────── 前置检查 ────────────────────────────
if [[ "$STANDALONE" == false ]]; then
    [[ ! -d "$RULES_SRC" ]]     && error "规范来源不存在: $RULES_SRC（规范仓库是否完整？）"
    [[ ! -f "$SETTINGS_SRC" ]]  && error "规范来源不存在: $SETTINGS_SRC"
    [[ ! -f "$CLAUDE_MD_SRC" ]] && error "规范来源不存在: $CLAUDE_MD_SRC"
fi

# --link 需要本地仓库，standalone 下无意义
if [[ "$STANDALONE" == true ]] && [[ "$MODE" == "link" ]]; then
    error "--link 模式需要本地 agent-development-specification 仓库，请改用 --copy 或默认 submodule 模式"
fi

# 确定 submodule 注册 URL（in-repo 时优先读 git remote，fallback 到硬编码 URL）
if [[ "$MODE" == "submodule" ]]; then
    if [[ "$STANDALONE" == false ]]; then
        REMOTE_URL="$(git -C "$SPEC_REPO" remote get-url origin 2>/dev/null)" \
            || REMOTE_URL="$SPEC_REPO_URL"
    else
        REMOTE_URL="$SPEC_REPO_URL"
    fi
fi

# standalone + copy：提前克隆规范仓库到临时目录
if [[ "$STANDALONE" == true ]] && [[ "$MODE" == "copy" ]]; then
    info "standalone 模式：克隆规范仓库（--depth=1）..."
    _TEMP_DIR="$(mktemp -d)"
    trap 'rm -rf "$_TEMP_DIR"' EXIT
    git clone --depth=1 "$SPEC_REPO_URL" "$_TEMP_DIR"
    RULES_SRC="${_TEMP_DIR}/${TEMPLATE_RULES_REL}"
    SETTINGS_SRC="${_TEMP_DIR}/${TEMPLATE_SETTINGS_REL}"
    CLAUDE_MD_SRC="${_TEMP_DIR}/${TEMPLATE_CLAUDE_MD_REL}"
    success "规范仓库克隆完成"
fi

# 目录不存在时自动创建
if [[ ! -d "$TARGET" ]]; then
    mkdir -p "$TARGET"
    info "创建目录: $TARGET"
fi

# 非 git 仓库时自动初始化
if [[ ! -d "${TARGET}/.git" ]]; then
    git -C "$TARGET" init
    success "初始化 Git 仓库: $TARGET"
fi

# ──────────────────────────── 开始安装 ────────────────────────────
echo ""
echo "目标项目 : $TARGET"
if [[ "$STANDALONE" == true ]]; then
    echo "规范仓库 : ${SPEC_REPO_URL} (standalone)"
else
    echo "规范仓库 : $SPEC_REPO"
fi
echo "模式     : $MODE"
echo ""

CLAUDE_DIR="${TARGET}/.claude"
TARGET_RULES="${CLAUDE_DIR}/rules"
TARGET_SETTINGS="${CLAUDE_DIR}/settings.json"

mkdir -p "$CLAUDE_DIR"

# ── 步骤 1：安装 .claude/rules/ ──────────────────────────────────

setup_submodule() {
    local submodule_dir="${TARGET}/${SUBMODULE_PATH}"

    # 检查是否已注册
    if [[ -f "${TARGET}/.gitmodules" ]] \
        && grep -qF "path = ${SUBMODULE_PATH}" "${TARGET}/.gitmodules"; then
        success "submodule '${SUBMODULE_PATH}' 已注册，执行 update --init 确保已检出"
        git -C "$TARGET" submodule update --init "$SUBMODULE_PATH"
    else
        info "添加 submodule: ${SUBMODULE_PATH} -> ${REMOTE_URL}"
        git -C "$TARGET" submodule add "$REMOTE_URL" "$SUBMODULE_PATH"
        success "添加 submodule 完成"
    fi

    # standalone 模式：子模块克隆完成后，从子模块目录获取模板文件
    if [[ "$STANDALONE" == true ]]; then
        SETTINGS_SRC="${TARGET}/${SUBMODULE_PATH}/${TEMPLATE_SETTINGS_REL}"
        CLAUDE_MD_SRC="${TARGET}/${SUBMODULE_PATH}/${TEMPLATE_CLAUDE_MD_REL}"
    fi

    # 建立相对符号链接 .claude/rules -> agent-development-specification/spec/project-templates/golang/.claude/rules
    if [[ -L "$TARGET_RULES" ]]; then
        current="$(readlink "$TARGET_RULES")"
        if [[ "$current" == "$RULES_LINK_TARGET" ]]; then
            success ".claude/rules 符号链接已正确指向子模块，无需更新"
            return
        fi
        if confirm_overwrite ".claude/rules（当前指向 ${current}）"; then
            rm "$TARGET_RULES"
        else
            info "跳过 .claude/rules 符号链接"; return
        fi
    elif [[ -d "$TARGET_RULES" ]]; then
        file_count="$(find "$TARGET_RULES" -maxdepth 1 -name "*.md" | wc -l)"
        if confirm_overwrite ".claude/rules/（目录，含 ${file_count} 个 .md 文件）"; then
            rm -rf "$TARGET_RULES"
        else
            info "跳过 .claude/rules 符号链接"; return
        fi
    elif [[ -e "$TARGET_RULES" ]]; then
        error ".claude/rules 已存在且类型未知，请手动处理"
    fi

    # 在 .claude/ 目录下创建相对符号链接，避免绝对路径问题
    ln -s "$RULES_LINK_TARGET" "$TARGET_RULES"
    success "创建相对符号链接: .claude/rules -> ${RULES_LINK_TARGET}"
}

setup_copy() {
    if [[ -d "$TARGET_RULES" ]]; then
        file_count="$(find "$TARGET_RULES" -maxdepth 1 -name "*.md" | wc -l)"
        if confirm_overwrite ".claude/rules/（目录，含 ${file_count} 个 .md 文件）"; then
            rm -rf "$TARGET_RULES"
        else
            info "跳过 .claude/rules"; return
        fi
    elif [[ -L "$TARGET_RULES" ]]; then
        if confirm_overwrite ".claude/rules（符号链接）"; then
            rm "$TARGET_RULES"
        else
            info "跳过 .claude/rules"; return
        fi
    elif [[ -e "$TARGET_RULES" ]]; then
        error ".claude/rules 已存在且类型未知，请手动处理"
    fi

    cp -r "$RULES_SRC" "$TARGET_RULES"
    copied_count="$(find "$TARGET_RULES" -maxdepth 1 -name "*.md" | wc -l)"
    success "复制规范文件到 .claude/rules/（共 ${copied_count} 个文件）"
}

setup_link() {
    if [[ -L "$TARGET_RULES" ]]; then
        current="$(readlink "$TARGET_RULES")"
        if [[ "$current" == "$RULES_SRC" ]]; then
            success ".claude/rules 符号链接已正确，无需更新"; return
        fi
        confirm_overwrite ".claude/rules（当前指向 ${current}）" && rm "$TARGET_RULES" || { info "跳过"; return; }
    elif [[ -d "$TARGET_RULES" ]]; then
        confirm_overwrite ".claude/rules/（目录）" && rm -rf "$TARGET_RULES" || { info "跳过"; return; }
    elif [[ -e "$TARGET_RULES" ]]; then
        error ".claude/rules 已存在且类型未知，请手动处理"
    fi

    ln -s "$RULES_SRC" "$TARGET_RULES"
    success "创建绝对路径符号链接: .claude/rules -> $RULES_SRC"
    warn ".claude/rules 使用绝对路径，不适合提交到 git 或跨机器使用"
}

case "$MODE" in
    submodule) setup_submodule ;;
    copy)      setup_copy ;;
    link)      setup_link ;;
esac

# ── 步骤 2：安装 .claude/settings.json ──────────────────────────────

install_settings() {
    if [[ -f "$TARGET_SETTINGS" ]]; then
        if confirm_overwrite ".claude/settings.json"; then
            cp "$SETTINGS_SRC" "$TARGET_SETTINGS"
            success "覆盖 .claude/settings.json"
        else
            info "跳过 .claude/settings.json"
        fi
    else
        cp "$SETTINGS_SRC" "$TARGET_SETTINGS"
        success "创建 .claude/settings.json"
    fi
}

install_settings

# ── 步骤 3：处理 CLAUDE.md ──────────────────────────────────────────
# 无论 CLAUDE.md 是否存在，都确保团队规范内容已追加（幂等）。
# 已存在时追加到文件末尾；不存在时以规范内容创建。
# 使用 <!-- dev-rules:begin/end --> 标记检测是否已追加过。

TARGET_CLAUDE="${TARGET}/CLAUDE.md"

append_team_standards() {
    if grep -qF "$DEV_RULES_BEGIN" "$TARGET_CLAUDE" 2>/dev/null; then
        # 已有区块：删除旧内容，随后重新写入（支持规范更新）
        local tmp
        tmp="$(mktemp)"
        awk -v begin="$DEV_RULES_BEGIN" -v end="$DEV_RULES_END" \
            '$0 == begin, $0 == end {next} {print}' \
            "$TARGET_CLAUDE" > "$tmp" \
            && mv "$tmp" "$TARGET_CLAUDE" \
            || { rm -f "$tmp"; error "更新 CLAUDE.md 失败"; }
    fi

    {
        echo ""
        echo ""
        echo "$DEV_RULES_BEGIN"
        echo "<!-- 以下内容由 install.sh 自动追加，来自 agent-development-specification 规范仓库 -->"
        echo "<!-- 请勿手动修改此区块；如需更新，重新运行 install.sh -->"
        echo ""
        cat "$CLAUDE_MD_SRC"
        echo ""
        echo "$DEV_RULES_END"
    } >> "$TARGET_CLAUDE"

    success "写入团队规范内容到 CLAUDE.md"
}

if [[ -f "$TARGET_CLAUDE" ]]; then
    info "CLAUDE.md 已存在，追加团队规范内容"
else
    info "CLAUDE.md 不存在，创建新文件"
fi
append_team_standards

# ──────────────────────────── 完成 ────────────────────────────
echo ""
echo "═══════════════════════════════════════"
echo " 安装完成！"
echo "═══════════════════════════════════════"
echo ""
echo "下一步："
echo "  1. 查看 CLAUDE.md，在团队规范区块之前添加项目特定约定"
echo "  2. 在项目中打开 Claude Code，规范将自动加载"
case "$MODE" in
    submodule)
        echo "  3. 提交变更: git add .gitmodules .claude/ CLAUDE.md && git commit"
        echo "  4. 其他成员 clone 后执行: git submodule update --init"
        ;;
    copy)
        echo "  3. 提交变更: git add .claude/rules/ .claude/settings.json CLAUDE.md && git commit"
        echo "  4. 规范更新时重新运行: $(basename "$0") $TARGET --copy -y"
        ;;
    link)
        echo "  3. 建议将 .claude/rules 加入 .gitignore（绝对路径不跨机器）"
        ;;
esac
echo ""
