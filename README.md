# snapjanitor

Lists VM snapshots in vCenter and removes those on the ESXi hosts listed in `hostnames.txt`.

- `scripts/snapjanitor.py` – the tool (`--dry-run`, `--yes`, `--hostnames-file`)
- `playbooks/snapjanitor.yml` – Ansible wrapper (dry run by default, `-e remove=true` to delete)

```
pip install -r requirements.txt
export VCENTER_HOST=... VCENTER_USER=... VCENTER_PASSWORD=...
cp hostnames.txt.example hostnames.txt
python3 scripts/snapjanitor.py --dry-run
```
