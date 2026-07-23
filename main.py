"""
main.py - Email Automation CLI Entry Point

Provides a command-line interface for sending bulk emails with
HTML templates, attachments, and scheduling support.

Usage:
    python main.py -s "Subject Line"
    python main.py -s "Subject" -c data/recipients.csv --dry-run
    python main.py -s "Subject" -S "2026-12-25 09:00"
"""

import argparse
import sys
import os
from typing import List, Dict, Any

from config import get_smtp_config
from utils import load_recipients, get_attachments, format_file_size
from template import load_template, render_template
from sender import send_bulk_emails
from scheduler import schedule_email, run_scheduler, parse_datetime
from logger import setup_logger


# ─── ANSI Colors for terminal output ────────────────────────────
class Colors:
    HEADER  = '\033[95m'
    BLUE    = '\033[94m'
    CYAN    = '\033[96m'
    GREEN   = '\033[92m'
    YELLOW  = '\033[93m'
    RED     = '\033[91m'
    END     = '\033[0m'
    BOLD    = '\033[1m'
    DIM     = '\033[2m'


# ─── ASCII Banner ───────────────────────────────────────────────
BANNER = f"""{Colors.CYAN}{Colors.BOLD}
    ╔══════════════════════════════════════════════╗
    ║          📧  EMAIL AUTOMATION  CLI           ║
    ║     ─────────────────────────────────────    ║
    ║      Send bulk emails with style & ease      ║
    ╚══════════════════════════════════════════════╝
{Colors.END}"""


def print_config_summary(smtp_config: dict, recipients_count: int,
                         attachments: list, subject: str):
    """Prints a formatted summary of the current configuration."""
    print(f"\n  {Colors.BOLD}── Configuration ──────────────────{Colors.END}")
    print(f"  {Colors.DIM}SMTP Server  :{Colors.END} {smtp_config['host']}:{smtp_config['port']}")
    print(f"  {Colors.DIM}Sender       :{Colors.END} {smtp_config['sender_name']} <{smtp_config['sender_email']}>")
    print(f"  {Colors.DIM}Subject      :{Colors.END} {subject}")
    print(f"  {Colors.DIM}Recipients   :{Colors.END} {recipients_count}")
    if attachments:
        total_size = sum(os.path.getsize(f) for f in attachments)
        print(f"  {Colors.DIM}Attachments  :{Colors.END} {len(attachments)} file(s) ({format_file_size(total_size)})")
        for att in attachments:
            size = format_file_size(os.path.getsize(att))
            print(f"               └─ {os.path.basename(att)} ({size})")
    else:
        print(f"  {Colors.DIM}Attachments  :{Colors.END} None")
    print()


def print_result_summary(result: dict, subject: str, mode: str):
    """Prints a formatted summary of send results."""
    total = result['total']
    success = result['success']
    failed = result['failed']

    print(f"\n  {Colors.BOLD}── Results ────────────────────────{Colors.END}")
    print(f"  {Colors.DIM}Mode         :{Colors.END} {mode}")
    print(f"  {Colors.DIM}Subject      :{Colors.END} {subject}")
    print(f"  {Colors.DIM}Total        :{Colors.END} {total}")
    print(f"  {Colors.GREEN}✓ Successful :{Colors.END} {success}")
    if failed > 0:
        print(f"  {Colors.RED}✗ Failed     :{Colors.END} {failed}")
        print(f"\n  {Colors.RED}Failed deliveries:{Colors.END}")
        for detail in result['details']:
            if detail['status'] == 'failed':
                print(f"    └─ {detail['email']}: {detail['error']}")
    else:
        print(f"  {Colors.GREEN}✗ Failed     : 0{Colors.END}")
    print(f"\n  {Colors.GREEN}{Colors.BOLD}Operation completed.{Colors.END}\n")


def main():
    """Main entry point for the Email Automation CLI."""
    print(BANNER)

    # ── 1. Parse arguments ──────────────────────────────────────
    parser = argparse.ArgumentParser(
        description="📧 Email Automation CLI — Send bulk emails with HTML templates",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py -s "Monthly Newsletter"
  python main.py -s "Update" -c contacts.csv -a docs/
  python main.py -s "Reminder" -S "2026-12-25 09:00"
  python main.py -s "Preview" --dry-run
        """
    )
    parser.add_argument("-c", "--csv", default="data/recipients.csv",
                        help="Path to recipients CSV (default: data/recipients.csv)")
    parser.add_argument("-t", "--template", default="templates/email.html",
                        help="Path to HTML template (default: templates/email.html)")
    parser.add_argument("-s", "--subject", required=True,
                        help="Email subject line (required)")
    parser.add_argument("-a", "--attachments", default="attachments/",
                        help="Directory containing attachments (default: attachments/)")
    parser.add_argument("-S", "--schedule",
                        help="Schedule time: 'YYYY-MM-DD HH:MM' (optional)")
    parser.add_argument("-d", "--delay", type=float, default=1.0,
                        help="Delay between emails in seconds (default: 1.0)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Preview first email without sending")

    args = parser.parse_args()

    # ── 2. Set up logging ───────────────────────────────────────
    logger = setup_logger()

    # ── 3. Load and validate SMTP config ────────────────────────
    print(f"  {Colors.BLUE}▸ Loading SMTP configuration...{Colors.END}")
    try:
        smtp_config = get_smtp_config()
        print(f"  {Colors.GREEN}  ✓ Configuration loaded{Colors.END}")
    except ValueError as e:
        print(f"  {Colors.RED}  ✗ Configuration error: {e}{Colors.END}")
        sys.exit(1)

    # ── 4. Load recipients from CSV ─────────────────────────────
    print(f"  {Colors.BLUE}▸ Loading recipients from {args.csv}...{Colors.END}")
    try:
        recipients = load_recipients(args.csv)
        if recipients.empty:
            print(f"  {Colors.RED}  ✗ No valid recipients found in {args.csv}{Colors.END}")
            sys.exit(1)
        print(f"  {Colors.GREEN}  ✓ Loaded {len(recipients)} recipient(s){Colors.END}")
    except Exception as e:
        print(f"  {Colors.RED}  ✗ Failed to load recipients: {e}{Colors.END}")
        sys.exit(1)

    # ── 5. Load HTML template ───────────────────────────────────
    print(f"  {Colors.BLUE}▸ Loading template from {args.template}...{Colors.END}")
    try:
        template = load_template(args.template)
        print(f"  {Colors.GREEN}  ✓ Template loaded{Colors.END}")
    except Exception as e:
        print(f"  {Colors.RED}  ✗ Failed to load template: {e}{Colors.END}")
        sys.exit(1)

    # ── 6. Check for attachments ────────────────────────────────
    print(f"  {Colors.BLUE}▸ Scanning attachments in {args.attachments}...{Colors.END}")
    attachments = get_attachments(args.attachments)
    if attachments:
        print(f"  {Colors.GREEN}  ✓ Found {len(attachments)} attachment(s){Colors.END}")
    else:
        print(f"  {Colors.DIM}  · No attachments found{Colors.END}")

    # Print configuration summary
    print_config_summary(smtp_config, len(recipients), attachments, args.subject)

    # ── 7. Dry-run mode ─────────────────────────────────────────
    if args.dry_run:
        print(f"  {Colors.YELLOW}{Colors.BOLD}── DRY RUN MODE ──────────────────{Colors.END}")
        first_row = recipients.iloc[0].to_dict()
        preview_html = render_template(template, first_row)

        print(f"  {Colors.DIM}Recipient :{Colors.END} {first_row.get('name', 'N/A')} <{first_row.get('email', 'N/A')}>")
        print(f"  {Colors.DIM}Subject   :{Colors.END} {args.subject}")
        print(f"\n  {Colors.BOLD}── Rendered HTML Preview ──────────{Colors.END}")
        # Show first 500 chars of rendered HTML
        preview = preview_html[:500]
        if len(preview_html) > 500:
            preview += f"\n  {Colors.DIM}... (truncated, {len(preview_html)} chars total){Colors.END}"
        print(f"  {preview}")
        print(f"\n  {Colors.YELLOW}No emails were sent (dry-run).{Colors.END}\n")
        sys.exit(0)

    # ── 8. Schedule mode ────────────────────────────────────────
    if args.schedule:
        try:
            send_time = parse_datetime(args.schedule)
            print(f"  {Colors.CYAN}⏰ Scheduling email send for {args.schedule}...{Colors.END}")

            def do_send():
                return send_bulk_emails(
                    smtp_config=smtp_config,
                    recipients=recipients,
                    subject=args.subject,
                    template=template,
                    attachments=attachments,
                    delay=args.delay,
                    logger=logger
                )

            schedule_email(do_send, send_time)
            run_scheduler()
        except ValueError as e:
            print(f"  {Colors.RED}  ✗ Scheduling error: {e}{Colors.END}")
            sys.exit(1)
        return

    # ── 9. Immediate send mode ──────────────────────────────────
    print(f"  {Colors.YELLOW}{Colors.BOLD}⚠  You are about to send {len(recipients)} email(s).{Colors.END}")
    confirm = input(f"  {Colors.YELLOW}   Proceed? (y/N): {Colors.END}").strip().lower()

    if confirm != 'y':
        print(f"\n  {Colors.RED}Operation cancelled by user.{Colors.END}\n")
        sys.exit(0)

    print(f"\n  {Colors.BLUE}{Colors.BOLD}Sending emails...{Colors.END}\n")
    try:
        result = send_bulk_emails(
            smtp_config=smtp_config,
            recipients=recipients,
            subject=args.subject,
            template=template,
            attachments=attachments,
            delay=args.delay,
            logger=logger
        )
        print_result_summary(result, args.subject, "Immediate Send")
    except Exception as e:
        print(f"\n  {Colors.RED}  ✗ Fatal error during send: {e}{Colors.END}")
        logger.error(f"Fatal error during bulk send: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
