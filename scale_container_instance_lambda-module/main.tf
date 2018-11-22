
resource "aws_lambda_function" "scale_ecs_cluster_container_instances_lambda" {
  filename         = "scaling_lambda.zip"
  function_name    = "scale_ecs_cluster_container_instances_lambda_${var.env}"
  role             = "${aws_iam_role.iam_role_for_scaling_container_instance_lambda.arn}"
  handler          = "publish_schedulable_container_metric.lambda_handler"
  source_code_hash = "${var.source_code_hash}"
  runtime          = "python3.6"
  timeout          = 60

  tags = {
    Environment = "${var.env}"
    Name        = "scale_ecs_cluster_container_instances_lambda_${var.env}"
    CreatedBy   = "terraform"
  }
}

resource "aws_cloudwatch_event_rule" "every_minutes" {
  name = "every-minutes"
  description = "Fires every minute"
  schedule_expression = "rate(1 minute)"
}

resource "aws_cloudwatch_event_target" "check_foo_every_five_minutes" {
  rule = "${aws_cloudwatch_event_rule.every_minutes.name}"
  target_id = "check_foo"
  arn = "${aws_lambda_function.scale_ecs_cluster_container_instances_lambda.arn}"
}

resource "aws_lambda_permission" "allow_cloudwatch_to_call_lambda" {
  statement_id = "AllowExecutionFromCloudWatch"
  action = "lambda:InvokeFunction"
  function_name = "${aws_lambda_function.scale_ecs_cluster_container_instances_lambda.function_name}"
  principal = "events.amazonaws.com"
  source_arn = "${aws_cloudwatch_event_rule.every_minutes.arn}"
}
