#!/usr/bin/env python3

import aws_cdk as cdk

from above_cdk_app.above_cdk_app_stack import AboveCdkAppStack


app = cdk.App()
AboveCdkAppStack(app, "above-cdk-app")

app.synth()
