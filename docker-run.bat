docker run -p 5000:5000 --mount type=bind,source=C:\Users\andy\.aws,target=/root/.aws,readonly ^
    --env AWS_PROFILE=tolaatweb^
    --env TOLAATCOM_MAJOR=20210715_150022^
    --env RECAPTCHA_PRIVATE_KEY=x^
    --env APP_SECRET_KEY=x^
    --env A_PASSWORD=x^
    --env G_PASSWORD=x^
    tolaat:latest