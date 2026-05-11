# Zami Daemon — Control Remoto del Pod

## Setup (una sola vez en el Web Terminal)

```bash
cd /workspace && git clone -b claude/ugc-profile-generator-PxVGb https://github.com/Se7en198/Zami-girls.git && bash Zami-girls/daemon/setup.sh
```

El setup pide el GitHub PAT una vez, lo guarda en `/workspace/.zami_pat` y lanza el daemon.

## Ver logs

```bash
tail -f /workspace/Zami-girls/daemon/daemon.log
```
