from app.services.email_service import send_email

if __name__ == "__main__":
    try:
        send_email(
            to_email="test@example.com",
            subject="Food Delivery System - Test Email",
            body="Hello! Mailtrap email integration is working.",
        )
        print("Test email sent successfully! Check your Mailtrap Sandbox inbox.")

    except Exception as error:
        print(f"Email test failed: {error}")