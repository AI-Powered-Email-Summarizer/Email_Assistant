from transformers import BartTokenizer, BartForConditionalGeneration

# Load BART tokenizer & model
tokenizer = BartTokenizer.from_pretrained("facebook/bart-large-cnn")
model = BartForConditionalGeneration.from_pretrained("facebook/bart-large-cnn")

def summarize_email(email_body):
    """Summarizes an email using the BART model."""
    inputs = tokenizer.encode("summarize: " + email_body, return_tensors="pt", max_length=1024, truncation=True)
    summary_ids = model.generate(inputs, max_length=200, min_length=50, num_beams=4, early_stopping=True)
    return tokenizer.decode(summary_ids[0], skip_special_tokens=True)
