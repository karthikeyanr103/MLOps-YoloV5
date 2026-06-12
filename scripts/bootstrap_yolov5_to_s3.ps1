param(
    [Parameter(Mandatory = $true)]
    [string]$Bucket,

    [string]$Region = "us-east-1",
    [string]$Key = "models/yolov5s.pt"
)

$ErrorActionPreference = "Stop"
$downloadUrl = "https://github.com/ultralytics/yolov5/releases/download/v7.0/yolov5s.pt"
$temporaryModel = Join-Path $env:TEMP "yolov5s.pt"

Write-Host "Downloading official pretrained YOLOv5s v7.0 weights..."
Invoke-WebRequest -Uri $downloadUrl -OutFile $temporaryModel

try {
    Write-Host "Uploading model to s3://$Bucket/$Key ..."
    aws s3 cp $temporaryModel "s3://$Bucket/$Key" --region $Region
    if ($LASTEXITCODE -ne 0) {
        throw "AWS CLI upload failed with exit code $LASTEXITCODE."
    }
    Write-Host "Upload complete. S3 should now trigger Lambda and CodeBuild."
}
finally {
    Remove-Item -LiteralPath $temporaryModel -Force -ErrorAction SilentlyContinue
}
