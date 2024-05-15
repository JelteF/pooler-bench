# This is bit of a mix between the dev and the prod config included with
# supavisor. It takes the perf settings of prod and the access settings of
# dev.
import Config
# Configure your database
config :supavisor, Supavisor.Repo,
  username: "postgres",
  password: "postgres",
  hostname: "localhost",
  database: "supavisor_dev",
  stacktrace: true,
  show_sensitive_data_on_connection_error: true,
  pool_size: 10

config :supavisor, SupavisorWeb.Endpoint,
  # Binding to loopback ipv4 address prevents access from other machines.
  # Change to `ip: {0, 0, 0, 0}` to allow access from other machines.
  http: [ip: {127, 0, 0, 1}, port: System.get_env("PORT", "4000")]

# Watch static and templates for browser reloading.
config :supavisor, SupavisorWeb.Endpoint,
  live_reload: [
    patterns: [
      ~r"priv/static/.*(js|css|png|jpeg|jpg|gif|svg)$",
      ~r"lib/supavisor_web/(live|views)/.*(ex)$",
      ~r"lib/supavisor_web/templates/.*(eex)$"
    ]
  ]

# Configures Elixir's Logger
config :logger, :console,
  format: "$time [$level] $message $metadata\n",
  level: :info,
  metadata: [:error_code, :file, :line, :pid, :project, :user, :mode, :type]

