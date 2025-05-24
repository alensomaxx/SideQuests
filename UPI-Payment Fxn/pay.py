import tkinter as tk
from tkinter import messagebox, scrolledtext
import qrcode
import urllib.parse
from io import BytesIO
import base64
import datetime
from PIL import Image, ImageTk

# --- Configuration  ---
MERCHANT_UPI_ID = "alensocreation@okhdfcbank" 
MERCHANT_NAME = "Costa Coffee"

# --- Helper Function to Generate UPI Link ---
def generate_upi_link(upi_id, name, amount):
    if not (upi_id and name and amount is not None and amount > 0):
        return None
    encoded_name = urllib.parse.quote(name)
    return f"upi://pay?pa={upi_id}&pn={encoded_name}&am={amount:.2f}&cu=INR"

# --- Helper Function to Generate QR Code as Base64 Image  ---
def generate_qr_code_image(data, size=250):
    """
    Generates a QR code for the given data and returns a PIL Image object.
    Args:
        data (str): The data to encode in the QR code (e.g., UPI link).
        size (int): Desired size of the QR code image in pixels.
    Returns:
        PIL.Image.Image: A PIL Image object of the QR code, or None if data is invalid.
    """
    if not data:
        return None
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
    # Resize the image to ensure consistent display
    img = img.resize((size, size), Image.Resampling.LANCZOS)
    return img

# --- Tkinter Application Class ---
class UPIGeneratorApp:
    def __init__(self, master):
        self.master = master
        master.title("Costa Coffee UPI Pay")
        master.geometry("500x700") # Set initial window size
        master.resizable(False, False) # Make window not resizable
        master.config(bg="#f0f4f8") # Light background

        # --- Styling ---
        self.font_large = ("Arial", 16, "bold")
        self.font_medium = ("Arial", 12)
        self.font_receipt = ("Consolas", 10)
        self.button_color = "#e67e22" # Amber-like
        self.button_fg = "white"

        # --- Header ---
        self.title_label = tk.Label(master, text="Costa Coffee UPI", font=("Arial", 20, "bold"), fg="#e67e22", bg="#f0f4f8")
        self.title_label.pack(pady=10)

        # --- Transaction Details Frame ---
        self.details_frame = tk.Frame(master, bg="#ffffff", bd=2, relief="groove")
        self.details_frame.pack(pady=10, padx=20, fill="x")

        tk.Label(self.details_frame, text="Enter Amount (INR):", font=self.font_medium, bg="#ffffff").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.amount_entry = tk.Entry(self.details_frame, font=self.font_medium, width=20, bd=2, relief="solid")
        self.amount_entry.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
        self.amount_entry.insert(0, "0.00") # Default value

        tk.Label(self.details_frame, text="Customer UPI ID (Optional):", font=self.font_medium, bg="#ffffff").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.customer_upi_entry = tk.Entry(self.details_frame, font=self.font_medium, width=20, bd=2, relief="solid")
        self.customer_upi_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        self.details_frame.grid_columnconfigure(1, weight=1) # Allow amount entry to expand

        # --- Buttons Frame ---
        self.buttons_frame = tk.Frame(master, bg="#f0f4f8")
        self.buttons_frame.pack(pady=10, padx=20, fill="x")

        self.qr_button = tk.Button(self.buttons_frame, text="Generate QR Code", command=self.generate_qr,
                                   font=self.font_medium, bg=self.button_color, fg=self.button_fg,
                                   activebackground="#d35400", activeforeground="white",
                                   relief="raised", bd=3, cursor="hand2")
        self.qr_button.pack(side="left", expand=True, fill="x", padx=5)

        self.request_button = tk.Button(self.buttons_frame, text="Send Request (UPI ID)", command=self.send_request,
                                        font=self.font_medium, bg=self.button_color, fg=self.button_fg,
                                        activebackground="#d35400", activeforeground="white",
                                        relief="raised", bd=3, cursor="hand2")
        self.request_button.pack(side="right", expand=True, fill="x", padx=5)

        # --- QR Code Display ---
        self.qr_frame = tk.Frame(master, bg="#f8f8f8", bd=2, relief="solid")
        self.qr_frame.pack(pady=10, padx=20, fill="x", expand=False)
        self.qr_frame.pack_forget() # Hide initially

        self.qr_label = tk.Label(self.qr_frame, text="Scan this QR Code to Pay", font=("Arial", 12, "bold"), bg="#f8f8f8", fg="#444")
        self.qr_label.pack(pady=5)

        self.qr_canvas = tk.Canvas(self.qr_frame, width=250, height=250, bg="white", bd=0, highlightthickness=0)
        self.qr_canvas.pack(pady=5)
        self.qr_image_tk = None # To hold the Tkinter PhotoImage

        self.upi_link_display = tk.Label(self.qr_frame, text="", font=("Arial", 8), fg="#666", wraplength=400, bg="#f8f8f8")
        self.upi_link_display.pack(pady=5)

        # --- Generate Receipt Button ---
        self.receipt_button = tk.Button(master, text="Generate Receipt", command=self.generate_receipt,
                                       font=self.font_medium, bg="#28a745", fg="white", # Green color for receipt
                                       activebackground="#218838", activeforeground="white",
                                       relief="raised", bd=3, cursor="hand2")
        self.receipt_button.pack(pady=10, padx=20, fill="x")
        self.receipt_button.pack_forget() # Hide initially

        # --- Receipt Display ---
        self.receipt_text_area = scrolledtext.ScrolledText(master, wrap=tk.WORD, font=self.font_receipt,
                                                         height=10, bg="#ffffff", bd=1, relief="solid")
        self.receipt_text_area.pack(pady=10, padx=20, fill="both", expand=True)
        self.receipt_text_area.config(state=tk.DISABLED) # Make it read-only
        self.receipt_text_area.pack_forget() # Hide initially

        # --- New Transaction Button ---
        self.new_transaction_button = tk.Button(master, text="New Transaction", command=self.reset_app,
                                                font=self.font_medium, bg="#6c757d", fg="white", # Grey color for reset
                                                activebackground="#5a6268", activeforeground="white",
                                                relief="raised", bd=3, cursor="hand2")
        self.new_transaction_button.pack(pady=10, padx=20, fill="x")

        # --- Internal state variables ---
        self.current_upi_link = None
        self.current_amount = 0.0
        self.payment_method = ""

    def show_message(self, message, type="info"):
        if type == "info":
            messagebox.showinfo("Information", message)
        elif type == "error":
            messagebox.showerror("Error", message)
        elif type == "success":
            messagebox.showinfo("Success", message)

    def generate_qr(self):
        try:
            amount_str = self.amount_entry.get()
            amount = float(amount_str)
            if amount <= 0:
                self.show_message("Please enter a valid amount greater than 0.", "error")
                return

            self.current_amount = amount
            self.current_upi_link = generate_upi_link(MERCHANT_UPI_ID, MERCHANT_NAME, self.current_amount)
            self.payment_method = "QR Code Scan"

            if self.current_upi_link:
                qr_img_pil = generate_qr_code_image(self.current_upi_link, size=250)
                self.qr_image_tk = ImageTk.PhotoImage(qr_img_pil)
                self.qr_canvas.delete("all")
                self.qr_canvas.create_image(0, 0, anchor=tk.NW, image=self.qr_image_tk)
                self.upi_link_display.config(text=f"THANK YOU!")
                #self.upi_link_display.config(text=f"UPI Link: {self.current_upi_link}")
                

                self.qr_frame.pack(pady=10, padx=20, fill="x", expand=False)
                self.receipt_button.pack(pady=10, padx=20, fill="x")
                self.receipt_text_area.pack_forget() # Hide receipt if visible
                self.show_message("QR Code generated successfully!", "success")
            else:
                self.show_message("Could not generate UPI link. Please check inputs.", "error")
        except ValueError:
            self.show_message("Invalid amount. Please enter a number.", "error")

    def send_request(self):
        try:
            amount_str = self.amount_entry.get()
            amount = float(amount_str)
            customer_upi_id = self.customer_upi_entry.get().strip()

            if amount <= 0:
                self.show_message("Please enter a valid amount greater than 0.", "error")
                return
            if not customer_upi_id:
                self.show_message("Please enter a customer UPI ID to send a request.", "error")
                return

            self.current_amount = amount
            self.current_upi_link = generate_upi_link(customer_upi_id, MERCHANT_NAME, self.current_amount) # Note: recipient is customer_upi_id
            self.payment_method = "UPI ID Request"

            if self.current_upi_link:
                self.show_message(f"Simulating request sent to {customer_upi_id} for ₹{self.current_amount:.2f}.", "info")
                self.qr_frame.pack_forget() # Hide QR if visible
                self.receipt_button.pack(pady=10, padx=20, fill="x")
                self.receipt_text_area.pack_forget() # Hide receipt if visible
            else:
                self.show_message("Could not generate UPI link for request. Please check inputs.", "error")
        except ValueError:
            self.show_message("Invalid amount. Please enter a number.", "error")

    def generate_receipt(self):
        if self.current_amount <= 0 or not self.current_upi_link:
            self.show_message("Please generate a QR code or send a request first.", "error")
            return

        # Prepare receipt details
        transaction_id = f"TXN{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}-{datetime.datetime.now().microsecond}"
        date_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        customer_upi_id = self.customer_upi_entry.get().strip() if self.customer_upi_entry.get().strip() else "N/A"

        receipt_content = f"""
        ------------------------------------------
                     Payment Receipt
        ------------------------------------------
        Shop:            {MERCHANT_NAME}
        Transaction ID:  {transaction_id}
        Date & Time:     {date_time}
        Amount:          ₹{self.current_amount:.2f}
        Payment Method:  {self.payment_method}
        Customer UPI ID: {customer_upi_id}
        ------------------------------------------
        Thank you for your purchase!
        ------------------------------------------
        """
        self.receipt_text_area.config(state=tk.NORMAL) # Enable writing
        self.receipt_text_area.delete(1.0, tk.END) # Clear previous content
        self.receipt_text_area.insert(tk.END, receipt_content)
        self.receipt_text_area.config(state=tk.DISABLED) # Disable writing again

        self.receipt_text_area.pack(pady=10, padx=20, fill="both", expand=True)
        self.qr_frame.pack_forget() # Hide QR after receipt
        self.receipt_button.pack_forget() # Hide generate receipt button
        self.show_message("Receipt generated!", "success")

    def reset_app(self):
        self.amount_entry.delete(0, tk.END)
        self.amount_entry.insert(0, "0.00")
        self.customer_upi_entry.delete(0, tk.END)
        self.qr_canvas.delete("all")
        self.upi_link_display.config(text="")
        self.receipt_text_area.config(state=tk.NORMAL)
        self.receipt_text_area.delete(1.0, tk.END)
        self.receipt_text_area.config(state=tk.DISABLED)

        # Hide elements
        self.qr_frame.pack_forget()
        self.receipt_button.pack_forget()
        self.receipt_text_area.pack_forget()

        # Reset internal state
        self.current_upi_link = None
        self.current_amount = 0.0
        self.payment_method = ""
        self.show_message("Application reset for new transaction.", "info")


if __name__ == "__main__":
    root = tk.Tk()
    app = UPIGeneratorApp(root)
    root.mainloop()