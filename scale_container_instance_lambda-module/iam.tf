resource "aws_iam_role" "iam_role_for_scaling_container_instance_lambda" {
  name = "iam-role-for-scaling-container-instance-lambda-${var.env}"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "",
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF
}

resource "aws_iam_role_policy_attachment" "ecs_full_access" {
  role = "${aws_iam_role.iam_role_for_scaling_container_instance_lambda.id}"
  policy_arn = "arn:aws:iam::aws:policy/AmazonECS_FullAccess"
}

resource "aws_iam_role_policy_attachment" "cloud_watch_full_access" {
  role = "${aws_iam_role.iam_role_for_scaling_container_instance_lambda.id}"
  policy_arn = "arn:aws:iam::aws:policy/CloudWatchFullAccess"
}

resource "aws_iam_role_policy_attachment" "lambda-default-policy" {
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaRole"
  role = "${aws_iam_role.iam_role_for_scaling_container_instance_lambda.id}"
}

resource "aws_iam_role_policy_attachment" "logs_full_access" {
  role = "${aws_iam_role.iam_role_for_scaling_container_instance_lambda.id}"
  policy_arn = "arn:aws:iam::aws:policy/CloudWatchLogsFullAccess"
}