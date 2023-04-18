# **STORI CHALLENGE MVP**

The following description is about the steps followed to complete the Stori Code Challenge. For that I use the technologies and versions, mentioned in the next set of bullet points:

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

The Stori Challenge is about to implement an MVP to read CSV files, process them and send an email with a summary about the CSV file processing.

In my version, I use a Golang local CLI app, to read and upload the CSV file to an S3 bucket, which has a Lambda trigger to fire up the Lambda function each time a new file is uploaded into the bucket.

The Lambda function, process the uploaded CSV file, store the record in a DynamoDB table, and create the email templates and send them using Simple Email Service (SES).

You can see the flow in a visual way in the next diagram picture

![AWS floachart](/images/flow_chart.png)

---

The steps followed were the next:

1. Create a S3 bucket in where to upload the CSV transaction files to process
2. Create a local Golang CLI app with two flags:
    1. **-f filename** To store from the terminal the CSV filename to upload
    2. **-b bucket** The bucket name in where to store the CSV file
3. Create an IAM Role with basic Lambda permissions
4. Create a Lambda function and attach to S3 as a trigger for each new file uploaded
5. Update the IAM Role to grant S3 read permissions on each new object created to process them with the Lambda function
6. Create a DynamoDB table
7. Update the IAM Role to grant write permissions on the DynamoDB tbale to put the records from the CSV
8. Create Simple Email Service Indentities to send the summary of the CSV file processing
9. Update the IAM Role to grant permissions on the SES service to send email to the specified recources (the identities)

---
## **1. CREATE AN S3 BUCKET**

Create and S3 bucket in the AWS region of your preference, with a unique name, and all the default values.

---
## **2. CREATE A LOCAL GOLANG CLI APP**

To build the local Golang CLI app, you need to have installed the Go compiler, at least the version 1.19.1. For more information on how to install Go, check this [link](https://go.dev/dl/).

Move to the subfolder named _file\_uploader/_, and execute the following command:

> go mod tidy

With that you can install all the dependent pakcages for the local Golang CLI app.

After you have all the necessary dependencies, you can run the Golang CLI app with the next command:

> go run main.go -f \<filename_to_upload\> -b \<bucket_name\>

If you want to create the binary instead running the app directly, you have to execute the following commands

> go build -o <binary_name_you_want> .
>
> ./<binary_name_you_want> -f \<filename_to_upload\> -b \<bucket_name\>

If after applied the before command, you got and error related about credentials, you have to install and configure the [AWS CLI](https://aws.amazon.com/cli/) tool.

If you got an error about permissions or access denied, you have to configure your programatic access credentials, for that you can follow this [link](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-configure.html).

---

## **3. CREATE AN IAM ROLE FOR THE LAMBDA FUNCTION**

From the AWS IAM console, select _Roles_ and then click on _Create role_. In the next window for _Select trusted entity_ leave the _AWS Service_ default value and for use case check the _Lambda_ option.

In the ext window filter in the Permissions policies for the value _AWSLambdaBasicExecutionRole_, check it a click next.

Enter a descriptive role name, _e.g._ __StoriCSVFileProcessingRole__,and click on _Create role_.

---
## **4. CREATE A LAMBDA FUNCTION AND ATTACHE IT AS AN S3 TRIGGER**

From the AWS Lambda console click on _Create function_, in the next window leave the _Author from scracht_ value, give a descriptive function name, _e.g._ **StoriCSVProcessorLambda**, for the runtime value select **Python 3.9**, and for the _Change fault execution role_ value in the search bar select the Role name you created in the previous step. Click on _Create function_ 

The python code for the Lamdba function is in the subfolder **lambda/** for this directory. You can copy and paste the function code and then deploy the code clicking on the _Deploy_ button from the _Lambda code_ tab.

Also, in the Lambda console to create the S3 trigger, in the _Function overview_ section click on _Add trigger_, search for S3 in the _Select a source_ search input, select **S3 aws storage**. In the next window search for the bucket name you created in the first step, leave the default value for the _Event types_ which is **All objects create events**, check the _Recursive information_ check box and click on __Add__

---
## **5. UPDATE THE IAM ROLE TO GRANT READ PERMISSION FOR EACH NEW S3 OBJECT**

Go to the AWS IAM dashboard, click on _Roles_ and filter for the Role name you choose in the step **3.**, click on _Add permissions_ and select _Create inline policy_.

In the next window, select the **JSON** tab for editing the policy, and paste the following policy template:
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

You only need to replace the _Resource_ value with the ARN of your bucket you created in step **1.**

Click on _Review policy_, give it a descriptive policy name and click on _Create policy_.

---
## **6. CREATE THE DYNAMODB TABLE**

To create the DynamoDB table in where you are going to store the records from the CSV file, you need to go to the DynamoDB Console and select create table.

When the new interface appears, applie the following values for the _Partiton key_ and _Sort key_ values:

* Partition Key
    * Partition key name: Id
    * Type: string
* Sort key
    * Sort key name: Date
    * Type: String

Leave all of the other default values and click on _Create table_

---

## **7. UPDATE THE IAM ROLE TO GRANT PERMISSION TO CREATE RECORDS IN THE DYNAMO DB TABLE**

Back again to the AWS IAM dashboard, click on _Roles_, select the role you created in the step **3.**. In the Role name details window, click on _Add permissions_ and select **Create inline policy**. In the next window select the **JSON** tab and paste the following policy template:

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

You only need to replace the _Resource_ value with the ARN of your DynamoDB table you created in the previous step.

Click on _Review policy_, give it a descriptive policy name and click on _Create policy_.

---

## **8. CREATE SES INDENTITIES TO SEND THE EMAILS**

For this step, you need to create and __SES Identity__, for that go to the SES Dashboadr, click on _Create identity_, select **Email address** for the _Identity details_, put you email address, and click on _Create Identity_.

You will receive a verificiation link in the email you specified, and have to verify your email clicking on the verification link.

## **9. UPDATE THE IAM ROLE TO GRANT SEND EMAILS PERMISSIONS**

Back again to the AWS IAM Dashboard, click on _Roles_, filter and select the role you created in the step **3.**. In the Role name details window click on _Add permissions_, and select _Create inline policy_. In the next window slick on the **JSON** view tab and paste the following policy template:

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

You will only need to replace the _Resource_ value with the ARN, or ARNs, of your identity or indentities you verified with the AWS SES verification links.

Click on _Review policy_, give it a descriptive policy name and click on _Create policy_.

---

 After you applied all the previous steps, each time you upload a CSV transaction file with the Golang CLI app, you will have stored your CSV files in an AWS S3 bucket, each time a new file is uploaded in the AWS S3 bucket you will fire up the Lambda function to process the transaction records, save each record in the AWS DynamodDB table, and generate a summary and send it in an email to the destinations you specified as your AWS SES indetities.