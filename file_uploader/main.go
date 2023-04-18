package main

import (
	"flag"
	"fmt"
	"log"
	"os"
	"strings"
	"time"

	"github.com/aws/aws-sdk-go/aws"
	"github.com/aws/aws-sdk-go/aws/session"
	"github.com/aws/aws-sdk-go/service/s3/s3manager"
)

var (
	bucket   string
	filename string
	region   string
)

func init() {
	flag.Usage = func() {
		fmt.Printf("Usage: %s -f <filename> -b <bucket_name> [-r aws-region]\n\n", os.Args[0])
		flag.PrintDefaults()
	}
}

func main() {
	flag.StringVar(&bucket, "b", "", "S3 bucket name in where you want to upload the file")
	flag.StringVar(&filename, "f", "", "File to upload in the bucket given for the flag -b")
	flag.StringVar(&region, "r", "us-east-1", "AWS Region in where you created your AWS Services to work with")

	flag.Parse()

	if bucket == "" || filename == "" {
		log.Printf("You have to indicate the file to upload and the bucket destination!\n\n")
		flag.Usage()
	}

	file, err := os.Open(filename)
	if err != nil {
		log.Fatalf("Error trying to open the file %q: %s\n", filename, err)
	}

	defer file.Close()

	sess, err := session.NewSession(
		&aws.Config{
			Region: aws.String(region),
		},
	)
	if err != nil {
		log.Fatalf("Error trying to creating a new AWS Session: %s\n", err)
	}

	uploader := s3manager.NewUploader(sess)

	filename = fmt.Sprintf("%s_%d.csv", strings.TrimSuffix(filename, ".csv"), time.Now().Unix())

	_, err = uploader.Upload(&s3manager.UploadInput{
		Bucket: aws.String(bucket),
		Key:    aws.String(filename),
		Body:   file,
	})

	if err != nil {
		log.Fatalf("Unable to upload %q to %q: %s\n\n", filename, bucket, err)
	} else {
		fmt.Printf("Successfully uploaded %q to %q\n", filename, bucket)
	}
}
