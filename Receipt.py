import customtkinter as ctk
from tkinter import filedialog, messagebox
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
import datetime as dt

class PDFReceiptGenerator(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("PDF Receipt Generator")

        # Define and initialize company details frame
        company_frame = ctk.CTkFrame(self)
        company_frame.pack(pady=10, padx=10, fill="x")

        ctk.CTkLabel(company_frame, text="Company Name:").grid(row=0, column=0, sticky="w")
        self.company_name = ctk.CTkEntry(company_frame, width=200)
        self.company_name.grid(row=0, column=1)

        ctk.CTkLabel(company_frame, text="Company Address:").grid(row=1, column=0, sticky="w")
        self.company_address = ctk.CTkEntry(company_frame, width=200)
        self.company_address.grid(row=1, column=1)

        ctk.CTkLabel(company_frame, text="Company Phone:").grid(row=2, column=0, sticky="w")
        self.company_phone = ctk.CTkEntry(company_frame, width=200)
        self.company_phone.grid(row=2, column=1)

        ctk.CTkLabel(company_frame, text="Company Email:").grid(row=3, column=0, sticky="w")
        self.company_email = ctk.CTkEntry(company_frame, width=200)
        self.company_email.grid(row=3, column=1)

        # Customer details frame initialization
        customer_frame = ctk.CTkFrame(self)
        customer_frame.pack(pady=10, padx=10, fill="x")

        ctk.CTkLabel(customer_frame, text="Customer Name:").grid(row=0, column=0, sticky="w")
        self.customer_name = ctk.CTkEntry(customer_frame, width=200)
        self.customer_name.grid(row=0, column=1)

        ctk.CTkLabel(customer_frame, text="Customer Address:").grid(row=1, column=0, sticky="w")
        self.customer_address = ctk.CTkEntry(customer_frame, width=200)
        self.customer_address.grid(row=1, column=1)

        ctk.CTkLabel(customer_frame, text="Customer Phone:").grid(row=2, column=0, sticky="w")
        self.customer_phone = ctk.CTkEntry(customer_frame, width=200)
        self.customer_phone.grid(row=2, column=1)

        ctk.CTkLabel(customer_frame, text="Customer Email:").grid(row=3, column=0, sticky="w")
        self.customer_email = ctk.CTkEntry(customer_frame, width=200)
        self.customer_email.grid(row=3, column=1)

        # Product/service details frame initialization
        product_frame = ctk.CTkFrame(self)
        product_frame.pack(pady=10, padx=10, fill="x")

        ctk.CTkLabel(product_frame, text="Product/Service Description:").grid(row=0, column=0, sticky="w")
        self.product_description = ctk.CTkEntry(product_frame, width=200)
        self.product_description.grid(row=0, column=1)

        ctk.CTkLabel(product_frame, text="Quantity:").grid(row=1, column=0, sticky="w")
        self.quantity = ctk.CTkEntry(product_frame, width=200)
        self.quantity.grid(row=1, column=1)

        ctk.CTkLabel(product_frame, text="Price Per Unit:").grid(row=2, column=0, sticky="w")
        self.price_per_unit = ctk.CTkEntry(product_frame, width=200)
        self.price_per_unit.grid(row=2, column=1)

        # Tax and discount initialization
        tax_discount_frame = ctk.CTkFrame(self)
        tax_discount_frame.pack(pady=10, padx=10, fill="x")

        ctk.CTkLabel(tax_discount_frame, text="Tax Rate (%):").grid(row=0, column=0, sticky="w")
        self.tax_rate = ctk.CTkEntry(tax_discount_frame, width=200)
        self.tax_rate.grid(row=0, column=1)

        ctk.CTkLabel(tax_discount_frame, text="Discount (%):").grid(row=1, column=0, sticky="w")
        self.discount = ctk.CTkEntry(tax_discount_frame, width=200)
        self.discount.grid(row=1, column=1)

        # Footer text initialization
        footer_frame = ctk.CTkFrame(self)
        footer_frame.pack(pady=10, padx=10, fill="x")

        ctk.CTkLabel(footer_frame, text="Footer Text:").grid(row=0, column=0, sticky="w")
        self.footer_text = ctk.CTkEntry(footer_frame, width=200)
        self.footer_text.grid(row=0, column=1)

        # Generate receipt frame
        generate_frame = ctk.CTkFrame(self)
        generate_frame.pack(pady=10, padx=10, fill="x")

        generate_button = ctk.CTkButton(
            generate_frame,
            text="Generate Receipt",
            command=self.generate_pdf_receipt,
        )
        generate_button.pack()

    def generate_pdf_receipt(self):
        try:
            company_name = self.company_name.get()
            company_address = self.company_address.get()
            company_phone = self.company_phone.get()
            company_email = self.company_email.get()

            customer_name = self.customer_name.get()
            customer_address = self.customer_address.get()
            customer_phone = self.customer_phone.get()
            customer_email = self.customer_email.get()

            product_description = self.product_description.get()
            quantity = int(self.quantity.get())
            price_per_unit = float(self.price_per_unit.get())

            tax_rate = float(self.tax_rate.get())
            discount = float(self.discount.get())

            footer_text = self.footer_text.get()

            # Calculate totals
            subtotal = quantity * price_per_unit
            tax = subtotal * (tax_rate / 100)
            discount_amount = subtotal * (discount / 100)
            total = subtotal + tax - discount_amount

            # Save PDF file
            file_path = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf")],
                initialfile=f"Receipt_{dt.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.pdf",
            )

            if not file_path:
                raise ValueError("No file path specified")

            c = canvas.Canvas(file_path, pagesize=letter)

            # Adding company details to the PDF
            company_section_y = 10 * inch
            c.drawString(1 * inch, company_section_y, f"Company: {company_name}")
            c.drawString(1 * inch, company_section_y - 0.5 * inch, f"Address: {company_address}")
            c.drawString(1 * inch, company_section_y - 1 * inch, f"Phone: {company_phone}")
            c.drawString(1 * inch, company_section_y - 1.5 * inch, f"Email: {company_email}")

            # Adding customer details
            customer_section_y = company_section_y - 2 * inch
            c.drawString(1 * inch, customer_section_y, f"Customer: {customer_name}")
            c.drawString(1 * inch, customer_section_y - 0.5 * inch, f"Address: {customer_address}")
            c.drawString(1 * inch, customer_section_y - 1 * inch, f"Phone: {customer_phone}")
            c.drawString(1 * inch, customer_section_y - 1.5 * inch, f"Email: {customer_email}")

            # Product/service details
            product_section_y = customer_section_y - 2 * inch
            c.drawString(1 * inch, product_section_y, f"Product/Service: {product_description}")
            c.drawString(1 * inch, product_section_y - 0.5 * inch, f"Quantity: {quantity}")
            c.drawString(1 * inch, product_section_y - 1 * inch, f"Price Per Unit: {price_per_unit:.2f}")

            # Financial details
            financial_section_y = product_section_y - 2 * inch
            c.drawString(1 * inch, financial_section_y, f"Subtotal: {subtotal:.2f}")
            c.drawString(1 * inch, financial_section_y - 0.5 * inch, f"Tax ({tax_rate}%): {tax:.2f}")
            c.drawString(1 * inch, financial_section_y - 1 * inch, f"Discount ({discount}%): {discount_amount:.2f}")
            c.drawString(1 * inch, financial_section_y - 1.5 * inch, f"Total: {total:.2f}")

            # Adding footer text
            footer_section_y = financial_section_y - 2 * inch
            c.drawString(1 * inch, footer_section_y, footer_text)

            c.showPage()
            c.save()

            messagebox.showinfo("Success", f"PDF receipt created successfully at {file_path}")
        except ValueError as ve:
            messagebox.showwarning("Warning", str(ve))
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

# Main application
if __name__ == "__main__":
    root = ctk.CTk()
    root.geometry("300x200")  # Set initial window size

    # Button to open the PDF receipt generator
    open_pdf_button = ctk.CTkButton(root, text="Open PDF Generator", command=lambda: PDFReceiptGenerator(root))
    open_pdf_button.pack(pady=20)  # Add some padding around the button

    root.mainloop()  # Start the event loop