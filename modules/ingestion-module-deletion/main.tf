resource "null_resource" "ingest" {
  triggers = {
    update_toggle = var.revision ? timestamp() : "no-update"

    destroy_command = join(" ", concat([
      "python3", "${path.module}/ingestion.py",
      var.host,
      var.resource_type
    ], [
      for k, v in merge(var.data_map, { Active = false }) : "${k}=${v}"
    ]))
  }

  provisioner "local-exec" {
    command = join(" ", concat([
      "python3", "${path.module}/ingestion.py",
      var.host,
      var.resource_type
    ], [
      for k, v in var.data_map : "${k}=${v}"
    ]))
  }

  provisioner "local-exec" {
    when    = destroy
    command = self.triggers.destroy_command
  }

  lifecycle {
    ignore_changes = [triggers["destroy_command"]]
  }
}
