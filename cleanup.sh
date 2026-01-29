#!/usr/bin/env bash
set -e

cat << "BANNER"

      ┌──────────────────────────────┐
      │    Fedora Cleanup Utility    │
      │        system hygiene        │
      └──────────────────────────────┘

BANNER

echo " • Cleaning package manager cache"
sudo dnf clean all

echo " • Removing unused packages"
sudo dnf autoremove -y

echo " • Trimming system logs (200MB max)"
sudo journalctl --vacuum-size=200M

echo " • Clearing user cache"
rm -rf ~/.cache/*

echo " • Clearing temporary directories"
sudo rm -rf /tmp/* /var/tmp/*

echo " • Cleaning Flatpak leftovers"
if command -v flatpak >/dev/null 2>&1; then
    flatpak uninstall --unused -y && flatpak repair
else
    echo "   Flatpak not present, skipping"
fi

echo " • Removing old crash dumps"
sudo rm -rf /var/lib/systemd/coredump/*

echo " • Ensuring SSD TRIM is enabled"
sudo systemctl enable --now fstrim.timer

cat << "FOOTER"

      ───────── Cleanup complete ─────────

FOOTER

df -h
