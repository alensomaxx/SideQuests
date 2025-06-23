# 💸 UPI Payment FXN — Instant QR & Request Generator

**UPI Payment FXN** is a sleek, interactive desktop utility built using **Python + Tkinter**, designed for merchants, small businesses, and creators who want to **quickly accept UPI payments**.  
It supports both **QR code generation** and **UPI ID payment requests**, complete with **real-time receipts**, clean visuals, and a seamless user experience.

---

## 🚀 Key Features

✅ **Instant QR Code Generator**  
Enter an amount and instantly generate a scannable QR code linked to your UPI ID.

📬 **Send UPI Payment Requests**  
Just enter the customer's UPI ID and amount — the app generates a ready-to-use UPI link for requesting payment.

🧾 **Real-Time Receipt Generator**  
After generating a QR or sending a request, receive a **timestamped digital receipt** with transaction details.

🎨 **Modern, Responsive UI**  
Polished interface using **Tkinter** — intuitive layouts, color-coded buttons, and smooth transitions.

💼 **Business Ready**  
Perfect for **cafes, kiosks, freelancers, delivery services, or small shops** that want to simplify digital payments.

🧠 **Built-in Validation & Feedback**  
Friendly alerts guide users through errors, successful actions, and completed transactions.

---


## ⚙️ How It Works

1. **Launch the App**  
   `python upi_payment_fxn.py`

2. **Enter Amount**  
   Type the amount (in INR) the customer needs to pay.

3. **(Optional) Add Customer UPI ID**  
   Add this if you'd like to send a UPI request instead of generating a QR.

4. **Choose an Action**  
   - Click **"Generate QR Code"** to create a scannable QR for payment.
   - Click **"Send Request (UPI ID)"** to generate a UPI link.

5. **View / Copy / Scan**
   - The app shows the QR (or simulates the request).
   - Click **"Generate Receipt"** to create a printable record.

6. **Start a New Transaction**  
   Hit **"New Transaction"** to reset everything and go again.

---

## 📋 Sample Receipt Output

```plaintext
------------------------------------------
             Payment Receipt
------------------------------------------
Shop:            Costa Coffee
Transaction ID:  TXN20250623150312-487973
Date & Time:     2025-06-23 15:03:12
Amount:          ₹180.00
Payment Method:  QR Code Scan
Customer UPI ID: N/A
------------------------------------------
Thank you for your purchase!
------------------------------------------

