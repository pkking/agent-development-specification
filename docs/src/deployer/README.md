# deployer/deploy.py

> K8s 预览部署器, 支持 4 种模式: dev-pod / data-pod / shared / none.

## 命令

- `deploy.py deploy --repo <repo> --pr <PR号>`
- `deploy.py promote --repo <repo> --env beta`
- `deploy.py cleanup --repo <repo> --pr <PR号>`
- `deploy.py status --repo <repo> --pr <PR号>`

## 关联

- [`../../pipeline/generic-layer/deployer.md`](../../pipeline/generic-layer/deployer.md)
- [`../../pipeline/project-layer/preview-service-yaml-spec.md`](../../pipeline/project-layer/preview-service-yaml-spec.md)
