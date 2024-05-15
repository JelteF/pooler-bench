#!/bin/bash

set -euxo pipefail

sudo tee /etc/apt/preferences.d/dotnet > /dev/null <<EOF
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

sudo add-apt-repository -y ppa:rabbitmq/rabbitmq-erlang

sudo apt-get update

sudo apt-get install -y dotnet-sdk-8.0 openjdk-17-jdk libevent-dev libssl-dev libc-ares-dev cmake gcc g++ make autoconf automake libtool pkg-config elixir erlang-dev erlang-xmerl erlang-os-mon inotify-tools
git clone https://github.com/pgbouncer/pgbouncer --recurse-submodules
git clone https://github.com/supabase/supavisor
git clone https://github.com/yandex/odyssey
git clone https://github.com/postgresml/pgcat
git clone https://github.com/citusdata/tools

git clone https://github.com/pgjdbc/pgjdbc
git clone https://github.com/npgsql/Npgsql

pip install docopt
cd pgbouncer
./autogen.sh
./configure --with-cares
make -j20
cd -

cd odyssey
make local_build
cd -

cd pgcat
cargo build --release
cd -

cd pgjdbc
./gradlew cleanTest
cd -

cp configs/supavisor.exs supavisor/config/bench.exs
cd supavisor
mix deps.get
MIX_ENV=bench mix compile
MIX_ENV=bench mix release supavisor
cd -
