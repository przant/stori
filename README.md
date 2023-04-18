# **STORI CHALLENGE MVP**

The following description is about the steps applied to complete the Stori Code Challenge. For that I use the technologies and versions, mentioned in the ext set of bullet points:

---

* Visual Studio Code
* Python version: Python 3.9.6
* Go version: go1.19.1 darwin/amd64
* OS MacOS: Monterrey version 12.6.5
* AWS CLI: AWS CLI v2 2.11.13 Python/3.11.3
* AWS Services: 
  * S3
  * Lambda
  * DynamoDB
  * Simple Email Service (SES)

---

The Stori Challenge is about to implement an MVP to read CSV files, process them and send an email with a summary about the file processing.

In my version, I use a Golang local CLI app, to read and upload the CSV file to an S3 bucket, which has a Lambda trigger to fire up the Lambda function each time a new file is uploaded into the bucket.

The Lambda function, process the uploaded CSV file, store the record in DynamoDB table, and create the email templates and send them using Simple Email Service (SES).

You can see the flow in a visual way in the next diagram picture

![AWS floachart](/images/flow_chart.png)

---

## **BUILD LOCAL GOLANG APP**

To build the Golang local app, you need to have installed the Go compiler, at least the version 1.19.1. For mre information on how to install Go, check thits [link](https://go.dev/dl/).

Move to the subfolder file uploader, and if you do not have installed the necessary AWS SDK packages for Golang, you have to execute the following command:

> go mod tidy

With that you can install all the dependent pakcages for the local Golang CLI app.

After you have all the necessary dependencies, you can run the Golang CLI app with the next command:

> go run main.go -f \<filename_to_upload\> -b \<bucket_name\>

If after applied the before command, you got and error related about credentials, you have to install and configure the [AWS CLI](https://aws.amazon.com/cli/) tool.

If you got an error about permissions or access denied, you need to check your S3 bucket access or create one with an AWS valid account.

---
## **CREATE AND ATTACH THE LAMBDA TRIGGER**

When you have your S3 bucket ready to upload files, you will need to create a Lambda function, for that go to the AWS Lambda console, clikc on create and select Python3.9 for the runtime, also you can create a new role o selected a exisiting one.

The python code for the Lamdba function is in the subfolder **lambda/** for this directory. You can copy and paste the function code and the deploy the conde in the Lambda console.

Also, in the Lambda console you need to create a trigger select the bucket you created before, and select all object creation an attache the trigger.

Aditionally, you will need to update yout IAM Role, addin a policy like the following:

~~~
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "S3ReadObjectsPermission",
            "Effect": "Allow",
            "Action": "s3:*Object",
            "Resource": "arn:aws:s3:::your_bucket_name/*"
        }
    ]
}
~~~

And with the previous steps, you can fire up your Lambda each time you uploaded a file in the S3 bucket.

## **CREATE THE DYNAMODB TABLE**

To create the DynamoDB table in where you will store the records from the CSV file, you need to go to the DynamoDB Console and select create table.

When the new interface appears, give a nae to the table, select Id of string type for the Partition Key and Date of type string for the Sort Key.

On you Role, the one you created when the Lambda fucntion was created, you need yo add a Polocy like this:

~~~
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "DDBWritePermission",
            "Effect": "Allow",
            "Action": "dynamodb:PutItem",
            "Resource": "arn:aws:dynamodb:your_region:your_account_num:table/YourTableName"
        }
    ]
}
~~~

With this, you have the DynamoDb table in where you can store the records from the csv file.

---

## **CONFIGURE THE SES TO SEND THE EMAILS**

For this step, you need to create and Indetity, select **Email address** for the type and put you email address.

Also, you have to add the necessary permissions to send the email on the email list you have verified in the AWS SES. The policy is like the following:

~~~
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "SendEmailPolicy",
            "Effect": "Allow",
            "Action": [
                "ses:SendEmail",
                "ses:SendRawEmail"
            ],
            "Resource": [
                "arn:aws:ses:your_region:your_account_num:identity/your_email"
            ]
        }
    ]
}
~~~

After you create the indetity, you will recevive an email with a verification link.

---

With al the previous steps you could run the app to process, store, and send emails. 