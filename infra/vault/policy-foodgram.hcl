path "secret/data/foodgram/*" {
  capabilities = ["read", "list"]
}
path "kvv2/data/foodgram/*" {
  capabilities = ["read", "list"]
}
path "secret/metadata/foodgram/*" {
  capabilities = ["read", "list"]
}
path "kvv2/metadata/foodgram/*" {
  capabilities = ["read", "list"]
}
path "sys/internal/ui/mounts/secret/foodgram/*" {
  capabilities = ["read"]
}
path "sys/internal/ui/mounts/kvv2/secret/data/foodgram/*" {
  capabilities = ["read"]
}
path "sys/internal/ui/mounts/kvv2/*" {
  capabilities = ["read"]
}
path "sys/internal/ui/mounts/secret" {
  capabilities = ["read"]
}
path "sys/mounts" {
  capabilities = ["read", "list"]
}
path "sys/mounts/*" {
  capabilities = ["read", "list"]
}
path "secret/data/foodgram/rabbitmq" {
  capabilities = ["read"]
}
path "secret/data/foodgram/database" {
  capabilities = ["read"]
}

