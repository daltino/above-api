# Above CDK App Stack

You should explore the contents of this project. It demonstrates a CDK app with an instance of a stack (`above_cdk_app_stack`)
which contains an Amazon SQS queue that is subscribed to an Amazon SNS topic.

The `cdk.json` file tells the CDK Toolkit how to execute your app.

This project is set up like a standard Python project. The initialization process also creates
a virtualenv within this project, stored under the .venv directory. To create the virtualenv
it assumes that there is a `python3` executable in your path with access to the `venv` package.
If for any reason the automatic creation of the virtualenv fails, you can create the virtualenv
manually once the init process completes.

To manually create a virtualenv on MacOS and Linux:

```
$ python3 -m venv .venv
```

After the init process completes and the virtualenv is created, you can use the following
step to activate your virtualenv.

```
$ source .venv/bin/activate
```

If you are a Windows platform, you would activate the virtualenv like this:

```
% .venv\Scripts\activate.bat
```

Once the virtualenv is activated, you can install the required dependencies.

```
$ pip install -r requirements.txt
```

At this point you can now synthesize the CloudFormation template for this code.

```
$ cdk synth
```

You can now begin exploring the source code, contained in the hello directory.
There is also a very trivial test included that can be run like this:

```
$ pytest
```

To add additional dependencies, for example other CDK libraries, just add to
your requirements.txt file and rerun the `pip install -r requirements.txt`
command.

## Useful commands

- `cdk ls` list all stacks in the app
- `cdk synth` emits the synthesized CloudFormation template
- `cdk deploy` deploy this stack to your default AWS account/region
- `cdk deploy --profile <AWS_PROFILE>` deploy this stack to selected AWS profile (account/region)
- `cdk diff` compare deployed stack with current state
- `cdk docs` open CDK documentation
- `cdk destroy` detroys the stack

## Testing the two endpoints

After deploying the entire CDK stack you can test the endpoints as follows:

### ListShoes

Send a GET request to https://<APIGW_ID>.execute-api.us-west-2.amazonaws.com/dev/shoes

This will run an insert into DynamoDB create records of shoes using the hardcoded values provided.

You can copy a valid `shoeID` from the list of shoes created and stored in DynamoDB

### CreateOrder

Send a POST request to https://<APIGW_ID>.execute-api.us-west-2.amazonaws.com/dev/orders

Use this sample payload for the request:

```
{
 "size": 42,
 "client": "Jane Doe",
 "shoeId": "<SHOE_ID_FROM_DYNAMODB>",
 "shippingInfo": {"Destination": " XYZ Street, XYZ 1234", "DeliveryDate": "2023-04-10 11:00:00"}
}
```

You should get back a 200 success messages: `{"message": "Order was created successfully"}`

Enjoy!
