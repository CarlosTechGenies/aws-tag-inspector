from playwright.sync_api import sync_playwright, Page
from helpers import process_aws_tags
from datetime import datetime
import re
import os

def handle_mfa(page: Page):
    """Handle MFA authentication if required."""
    # Check if MFA is required
    # Wait briefly for MFA screen to appear
    page.wait_for_timeout(2000)
    mfa_required = page.get_by_role("radio", name="Authenticator app").is_visible()
    
    if mfa_required:
        print("MFA authentication required")
        # Check if we have authenticator app option
        page.get_by_label("Authenticator app").check()
        page.get_by_test_id("mfa-continue-button").click()
        mfa_code = input("Enter your MFA code: ")
        page.get_by_placeholder("enter code").fill(mfa_code)
        page.get_by_test_id("mfa-submit-button").click()
        page.wait_for_load_state("networkidle")
        print("MFA authentication completed")
    else:
        print("No MFA required, continuing...")

def get_available_regions(page: Page):
    """Get list of available AWS regions from the dropdown."""
    regions = []
    page.get_by_role("button", name="Select regions").click()
    page.wait_for_selector(".awsui_dropdown_qwoo0_1n520_149[aria-hidden='false']", state="visible", timeout=30000)
    region_elements = page.get_by_role("option").all()
    
    for elem in region_elements:
        region_text = elem.text_content().strip()
        if region_text and region_text != "All regions":
            regions.append(region_text)

    page.get_by_role("button", name="Select regions").click()
    
    return regions

def select_regions(page: Page):
    """Enhanced region selection with multi-region support."""
    # Present options to the user
    print("\nRegion Selection Options:")
    print("1. Use all regions (default)")
    print("2. Specify a single region")
    #print("3. Specify multiple regions")
    choice = input("Choose an option (1 or 2): ").strip()
    
    # Get available regions
    regions = get_available_regions(page)
    
    if choice == "1":
        # Use all regions
        print("Using all regions")
        # Open region dropdown
        page.get_by_role("button", name="Select regions").click()
        page.wait_for_selector(".awsui_dropdown_qwoo0_1n520_149[aria-hidden='false']", state="visible", timeout=30000)
        page.get_by_role("option", name="All regions").click()
    
    elif choice == "2":
        # Show available regions
        print("\nAvailable regions:")
        for i, region in enumerate(regions):
            print(f"{i+1}. {region}")
        
        # Let user choose a region
        region_choice = input("Enter the number or name of the region: ").strip()
        
        # Determine if user entered a number or name
        selected_region = None
        if region_choice.isdigit() and 1 <= int(region_choice) <= len(regions):
            selected_region = regions[int(region_choice) - 1]
        else:
            selected_region = region_choice
            
        print(f"Selecting region: {selected_region}")
        page.locator("[data-test='regionFilter']").filter(has=page.locator("text=us-east-2")).click()
        page.get_by_role("button", name="Select regions").click()
        page.wait_for_selector(".awsui_dropdown_qwoo0_1n520_149[aria-hidden='false']", state="visible", timeout=30000)
        page.get_by_role("option", name=selected_region).click()
    

    # This option is under development
    # elif choice == "3":
    #     # Show available regions for multi-selection
    #     print("\nAvailable regions:")
    #     for i, region in enumerate(regions):
    #         print(f"{i+1}. {region}")
        
    #     region_input = input("Enter region numbers or names separated by commas (e.g., 1,3,5 or us-east-1,eu-west-1): ").strip()
    #     region_choices = [choice.strip() for choice in region_input.split(',')]
        
    #     selected_regions = []
    #     for choice in region_choices:
    #         if choice.isdigit() and 1 <= int(choice) <= len(regions):
    #             selected_regions.append(regions[int(choice) - 1])
    #         else:
    #             selected_regions.append(choice)
        
    #     print(f"Selecting regions: {', '.join(selected_regions)}")
    #     page.get_by_role("option", name="All regions").click()
 
    #     for region in selected_regions:
    #         page.get_by_role("option", name=region).click()

def export_tags(page: Page, aws_username: str, region_info: str = "all"):
    """Export tags and save the CSV file."""

    page.locator("[data-test=\"showResults\"]").click()    
    print("Waiting for results to load (this may take several minutes)...")
    try:
        page.wait_for_selector("button[aria-label*='Export to CSV']:not([disabled])", state="visible", timeout=300000)  # 5 minutes
    except:
        print("Warning: Export button not enabled after timeout. Results may be incomplete.")
        if not page.is_visible("button[aria-label*='Export to CSV']"):
            print("Export button not found. Cannot continue with export.")
            return
    
    # Export to CSV
    print("Exporting to CSV...")
    with page.expect_download() as download_info:
        page.get_by_role("button", name=re.compile("Export.*CSV")).click()
        page.wait_for_selector(".awsui_dropdown_qwoo0_1n520_149[aria-hidden='false']", state="visible", timeout=60000)
        page.get_by_role("menuitem", name="Export all tags").click()

    download = download_info.value
    print("Download started...")
    folder_name = "tags_services_account"
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    
    current_date = datetime.now().strftime("%Y%m%d")
    new_filename = f"{aws_username}_{region_info}_{current_date}.csv"
    destination_path = os.path.join(folder_name, new_filename)
    download_path = download.path()

    print("Processing CSV with custom tag logic...")
    process_aws_tags(download_path, destination_path)
    print(f"Processed CSV saved to {destination_path}")
    os.remove(download_path)
    print("Done exporting and processing tags.")

def run(playwright):
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context(locale="python-sync")
    page = context.new_page()

    aws_account_id = input("Enter Account ID: ")
    aws_username = input("Enter your IAM username:")
    aws_password = input("Enter your IAM password:")

    print("Navigating to AWS sign-in page...")
    page.goto("https://signin.aws.amazon.com/")
    
    # Click Sign In if needed
    if page.is_visible("text=Sign In"):
        page.get_by_role("link", name="Sign In").click()
    
    print("Entering credentials...")
    page.locator("#account").fill(aws_account_id)
    page.wait_for_timeout(1000)
    page.locator("#username").fill(aws_username)
    page.wait_for_timeout(1000)
    page.locator("#password").fill(aws_password)
    page.wait_for_timeout(1000)
    page.locator("#signin_button").click()
    
    # Wait for login to complete
    print("Waiting for login...")
    
    # Handle MFA if required
    handle_mfa(page)
    
    # Navigate to Resource Groups & Tag Editor
    print("Navigating to Resource Groups & Tag Editor...")
    page.locator("#awsc-concierge-input").fill("Resource Groups & Tag Editor")
    page.wait_for_timeout(1000)
    
    # Wait for search results and click on Resource Groups
    page.wait_for_selector("[data-testid='services-search-result-link-resource-groups']", state="visible", timeout=10000)
    page.get_by_test_id("services-search-result-link-resource-groups").click()
    page.get_by_role("link", name="Tag Editor").click()

    select_regions(page)
    print("Selecting all resource types...")
    page.get_by_label("Resource types", exact=True).click()
    page.get_by_text("All supported resource types").click()

    export_tags(page, aws_username)
    print("Closing browser...")
    browser.close()

if __name__ == "__main__":
    with sync_playwright() as playwright:
        run(playwright)