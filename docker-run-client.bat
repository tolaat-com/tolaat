docker run -p 5005:5005 --mount type=bind,source=C:\Users\andy\.aws,target=/root/.aws,readonly ^
    --env TOLAATCOM_MAJOR=20210715_150022^
    --env RECAPTCHA_PRIVATE_KEY=x^
    --env APP_SECRET_KEY=x^
    --env A_PASSWORD=x^
    --env G_PASSWORD=x^
    --env SERVER=0^
    --env PORT=5005^
    --env HOST=0.0.0.0^
    tolaat:latest