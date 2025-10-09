# app.py
import streamlit as st
import os
import uuid
import boto3
from botocore.exceptions import ClientError
from config import LOCAL_STORAGE, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, S3_BUCKET, S3_REGION, SIGNED_URL_EXPIRY
from watermark.watermark import add_watermark
from utils.email_sender import send_delivery_email
from utils.tracker import log_event, read_events

st.set_page_config(page_title="PatternProtect MVP", layout="centered")
st.title("PatternProtect — MVP (watermark & deliver PDFs)")

st.markdown(
    """
    Upload pattern PDF, enter buyer info, and generate a buyer-specific watermarked PDF.
    This MVP supports local storage by default. In the next version files will be uploaded to secured cloud storage and signed URLs will be used.
    """
)

# Upload form
with st.form("upload_form"):
    seller_name = st.text_input("Seller name", value="Seller")
    pattern_name = st.text_input("Pattern name", value="My Pattern")
    uploaded_file = st.file_uploader("Upload pattern PDF", type=["pdf"])
    buyer_name = st.text_input("Buyer name (for watermark)")
    buyer_email = st.text_input("Buyer email (for delivery)")
    license_type = st.selectbox("License type", ["Personal", "Commercial", "Other"])
    expiry_hours = st.number_input("Download link expiry (hours, if using S3)", min_value=1, max_value=168, value=24)
    submit = st.form_submit_button("Generate & Deliver")

if submit:
    if not uploaded_file:
        st.error("Please upload a PDF file.")
    elif not buyer_email or not buyer_name:
        st.error("Please provide buyer name and buyer email.")
    else:
        tmp_input_path = os.path.join(LOCAL_STORAGE, f"tmp_{uuid.uuid4().hex}_in.pdf")
        tmp_out_name = f"{pattern_name}_{buyer_name}_{uuid.uuid4().hex}.pdf".replace(" ", "_")
        tmp_output_path = os.path.join(LOCAL_STORAGE, tmp_out_name)

        # Save input pdf locally
        with open(tmp_input_path, "wb") as f:
            f.write(uploaded_file.read())

        st.info("Generating watermarked PDF...")
        try:
            add_watermark(tmp_input_path, tmp_output_path, buyer_name, license_type, extra_id=str(uuid.uuid4())[:8])
            st.success("Watermark generated.")
        except Exception as e:
            st.error(f"Watermarking failed: {e}")
            raise

        # Upload to S3 if credentials present, else keep local
        download_link = None
        if AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY and S3_BUCKET:
            try:
                s3 = boto3.client(
                    "s3",
                    aws_access_key_id=AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                    region_name=S3_REGION
                )
                s3_key = f"patternprotect/{seller_name}/{tmp_out_name}"
                s3.upload_file(tmp_output_path, S3_BUCKET, s3_key)
                # generate presigned url
                download_link = s3.generate_presigned_url(
                    ClientMethod="get_object",
                    Params={"Bucket": S3_BUCKET, "Key": s3_key},
                    ExpiresIn=expiry_hours * 3600
                )
                st.success("Uploaded to S3 and generated signed URL.")
            except ClientError as e:
                st.warning(f"S3 upload failed; falling back to local file. Error: {e}")
                download_link = f"file://{os.path.abspath(tmp_output_path)}"
        else:
            download_link = f"file://{os.path.abspath(tmp_output_path)}"
            st.info("S3 not configured — file available locally. You can copy the path below.")

        #st.write("Download link:")
        #st.code(download_link)
        st.success("Watermarked PDF ready!")

        with open(tmp_output_path, "rb") as f:
           st.download_button(
              label="⬇️ Download Watermarked PDF",
              data=f,
              file_name=tmp_out_name,
              mime="application/pdf"
           )

        # Try to send email
        sent = send_delivery_email(buyer_email, buyer_name, download_link, pattern_name, expiry_hours)
        if sent:
            st.success(f"Delivery email sent to {buyer_email}.")
            log_event(seller_name, pattern_name, buyer_name, buyer_email, license_type, event="delivered", notes="email_sent")
        else:
            st.info("Email not sent automatically. You can copy the link and email the buyer manually.")
            log_event(seller_name, pattern_name, buyer_name, buyer_email, license_type, event="delivered", notes="email_fallback")

# Show recent events as simple dashboard
st.header("Recent deliveries / events")
df = read_events(limit=200)
if df is None or df.empty:
    st.info("No events logged yet.")
else:
    st.dataframe(df)

st.header("Share your feedback")

with st.form("feedback_form"):
    feedback_name = st.text_input("Your name (optional)")
    feedback_email = st.text_input("Your email (optional)")
    feedback_text = st.text_area("Your feedback / suggestions")
    submit_feedback = st.form_submit_button("Submit Feedback")

if submit_feedback:
    if feedback_text.strip() == "":
        st.warning("Please enter some feedback before submitting.")
    else:
        # Log the feedback using your existing logger
        log_event(
            seller_name=feedback_name or "Anonymous",
            pattern_name="Feedback",
            buyer_name=feedback_name or "Anonymous",
            buyer_email=feedback_email,
            license_type="N/A",
            event="feedback",
            notes=feedback_text
        )
        st.success("Thank you! Your feedback has been recorded.")
