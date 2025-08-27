import os
import subprocess
from datetime import datetime
from bs4 import BeautifulSoup
import requests
import phonenumbers
from phonenumbers import geocoder, carrier
from phonenumbers.phonenumberutil import NumberParseException


# ---------- Sherlock Search ----------
def run_sherlock(username, output_file):
    """
    Runs Sherlock for username search.
    """
    print(f"[*] Running Sherlock for username: {username}...")
    try:
        subprocess.run(['sherlock', '--version'], check=True, capture_output=True)

        command = ['sherlock', username, '--output', output_file, '--csv']
        print(f"[*] Executing command: {' '.join(command)}")

        subprocess.run(command, check=True, text=True)

    except FileNotFoundError:
        print("[!] Sherlock not found. Install it: https://github.com/sherlock-project/sherlock")
        return False
    except subprocess.CalledProcessError as e:
        print(f"[!] Error running Sherlock: {e}")
        return False
    except Exception as e:
        print(f"[!] Unexpected error: {e}")
        return False

    return True


# ---------- IGNOU Scraping ----------
def scrape_ignou_website(roll_number):
    """Scrapes IGNOU website for roll number (dummy example)."""
    if not roll_number or roll_number.lower() == "null":
        return "No roll number provided by user."

    print(f"[*] Scraping IGNOU website for roll number: {roll_number}...")
    url = "https://www.ignou.ac.in/results"
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        # Placeholder - adapt to real HTML
        return f"Roll Number {roll_number} possibly found in results."
    except requests.exceptions.RequestException as e:
        return f"[!] Failed to access IGNOU website: {e}"


# ---------- Phone Lookup ----------
def get_phone_number_details(phone_number):
    """Analyzes phone number details."""
    if not phone_number or phone_number.lower() == "null":
        return "No phone number provided."

    print(f"[*] Analyzing phone number: {phone_number}")
    try:
        parsed_number = phonenumbers.parse(phone_number)

        if not phonenumbers.is_valid_number(parsed_number):
            return "[!] Invalid phone number."

        country = geocoder.description_for_number(parsed_number, "en")
        service_provider = carrier.name_for_number(parsed_number, "en")
        number_type = phonenumbers.number_type(parsed_number)
        is_mobile = number_type == phonenumbers.PhoneNumberType.MOBILE

        details = f"""
### Phone Number Details
- **Full Number:** {phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.E164)}
- **Country:** {country}
- **Service Provider:** {service_provider if service_provider else 'Unknown'}
- **Is Mobile:** {"Yes" if is_mobile else "No"}
        """.strip()

        return details

    except NumberParseException as e:
        return f"[!] Could not parse phone number: {e}"
    except Exception as e:
        return f"[!] Unexpected error: {e}"


# ---------- Report Generator ----------
def generate_report(target, sherlock_output_file, ignou_info, phone_info=None):
    """Generates a Markdown report in README.md."""
    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    report_content = f"# OSINT Report for {target}\n\n"
    report_content += f"**Date of Report:** {date}\n\n"
    report_content += "---\n\n"

    # Sherlock
    report_content += "## Social Media and Username Findings\n\n"
    sherlock_csv_file = sherlock_output_file.replace('.txt', '.csv')
    if os.path.exists(sherlock_csv_file):
        with open(sherlock_csv_file, 'r', encoding="utf-8") as f:
            sherlock_results = f.read()
            report_content += "```csv\n" + sherlock_results + "\n```\n\n"
    else:
        report_content += "No Sherlock results found.\n\n"

    report_content += "---\n\n"

    # IGNOU
    report_content += "## Website & Other Findings\n\n"
    report_content += f"**IGNOU Website Search:** {ignou_info}\n\n"

    # Phone
    if phone_info:
        report_content += "---\n\n"
        report_content += "## Phone Number Analysis\n\n"
        report_content += phone_info + "\n\n"

    # Save
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(report_content)

    print("[+] OSINT report generated: README.md")


# ---------- Main Flow ----------
def main():
    print("===== OSINT TOOL =====")
    target = input("Enter a username, email, or phone number: ").strip()
    roll_number = input("Enter IGNOU roll number (or type 'null' if unknown): ").strip()
    phone_number = input("Enter phone number with country code (or type 'null' if unknown): ").strip()

    if not target:
        print("[-] No target provided. Exiting.")
        return

    sherlock_file = "not_applicable.txt"
    ignou_results = scrape_ignou_website(roll_number)
    phone_info = get_phone_number_details(phone_number)

    # Username search
    if len(target) > 3 and " " not in target and "." not in target and not target.isdigit():
        sherlock_file = f"{target}.txt"
        if run_sherlock(target, sherlock_file):
            print("[+] Sherlock finished.")

    generate_report(target, sherlock_file, ignou_results, phone_info)


if __name__ == "__main__":
    main()
