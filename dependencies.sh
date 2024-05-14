#!/bin/bash

sudo cat > /etc/apt/preferences.d/dotnet.conf <<EOF
Package: dotnet* aspnet* netstandard*
Pin: origin "archive.ubuntu.com"
Pin-Priority: -10

Package: dotnet* aspnet* netstandard*
Pin: origin "security.ubuntu.com"
Pin-Priority: -10
EOF


# Get OS version info
source /etc/os-release

# Download Microsoft signing key and repository
wget https://packages.microsoft.com/config/$ID/$VERSION_ID/packages-microsoft-prod.deb -O packages-microsoft-prod.deb

# Install Microsoft signing key and repository
sudo dpkg -i packages-microsoft-prod.deb

# Clean up
rm packages-microsoft-prod.deb

# Update packages
sudo apt-get update

sudo apt-get install -y dotnet-sdk-8.0 openjdk-17-jdk

git clone https://github.com/pgbouncer/pgbouncer
git clone https://github.com/supabase/supavisor
git clone https://github.com/yandex/odyssey
git clone https://github.com/postgresml/pgcat
git clone https://github.com/citusdata/tools

git clone https://github.com/pgjdbc/pgjdbc
git clone https://github.com/npgsql/Npgsql
