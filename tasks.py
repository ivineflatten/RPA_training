from robocorp.tasks import task
from robocorp import browser
from RPA.HTTP  import HTTP
from RPA.Tables import Tables
from RPA.PDF import PDF
from RPA.Archive import Archive
import shutil

# fs = FileSystem()


page = browser.page()
# pdf_file = ""

@task
def order_robots_from_RobotSpareBin():
    """ Orders robots from RobotSpareBin Industries Inc.
    Saves the order HTML receipt as a PDF file.
    Saves the screenshot of the ordered robot.
    Embeds the screenshot of the robot to the PDF receipt.
    Creates ZIP archive of the receipts and the images.
    """

    open_order_website()
    close_annoying_modal()
    get_orders()
    archive_receipts()
    clean_up()
    


def open_order_website():
    browser.goto("https://robotsparebinindustries.com/#/robot-order")
    # browser.configure()

def close_annoying_modal():
    page.click("button:text('OK')")
    

def get_orders():
    http = HTTP()
    http.download(url="https://robotsparebinindustries.com/orders.csv", overwrite=True)

    libraries = Tables()
    orders = libraries.read_table_from_csv("orders.csv", header=True)
    # customers = libraries.group_table_by_column(orders, "mail")
    for order in orders:
        fill_the_form(order)
        submit_order()
        store_receipt_as_pdf( order ["Order number"])

def fill_the_form(row):
    page.select_option("#head.custom-select", row["Head"])
    page.set_checked("#id-body-1", row["Body"])
    page.set_checked("#id-body-2", row["Body"])
    page.set_checked("#id-body-3", row["Body"])
    page.set_checked("#id-body-4", row["Body"])
    page.set_checked("#id-body-5", row["Body"])
    page.set_checked("#id-body-6", row["Body"])
    page.fill(str("input.form-control[placeholder='Enter the part number for the legs']"), row["Legs"])
    page.fill("#address", row["Address"])
    # page.click("#order")

def submit_order():
    page.click("#order")
    page.wait_for_timeout(2000)
    while True:
        if page.locator("div.alert.alert-danger[role='alert']"). is_visible():
            page.click("#order")
            # page.wait_for_timeout(2000)
        else:
            break

        

def store_receipt_as_pdf(order_number):
    pdf = PDF()
    receipt = page.locator("#receipt").inner_html()
    # receipt_name = f'"output/receipt/{order_number}.pdf"
    pdf_file = f"output/receipt/{order_number}.pdf"
    pdf.html_to_pdf(receipt, pdf_file)

    shot = screenshot_robot(order_number)
    embed_screenshot_to_receipt(shot, pdf_file)
    page.click("#order-another")
    page.click("button:text('OK')")
    return pdf_file


def screenshot_robot(order_number):
    robot = page.locator("#robot-preview-image")
    screenshot = f"output/image/{order_number}.png"
    robot.screenshot(path= screenshot)
    return screenshot 

def embed_screenshot_to_receipt(screenshot, pdf_file):
    pdf = PDF()
    pdf.add_files_to_pdf(files= [screenshot], target_document=pdf_file, append=True)

def archive_receipts():
    lib = Archive()
    lib.archive_folder_with_zip("output/receipt", "output/receipts.zip")
    lib.archive_folder_with_zip("output/image", "output/images.zip")

def clean_up():
    shutil.rmtree("output/receipt")
    shutil.rmtree("output/image")
    




    



