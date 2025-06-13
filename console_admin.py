
"""
Console administration tools for SPEAKYZ bot.
Allows managing subscriptions and users via console commands.
"""

import sys
import threading
import time
from models import User, get_db
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

def console_help():
    """Show available console commands."""
    print("\n" + "="*50)
    print("SPEAKYZ BOT ADMIN CONSOLE")
    print("="*50)
    print("Available commands:")
    print("  help - Show this help")
    print("  users - List all users")
    print("  stats - Show bot statistics")
    print("  add_sub <username> <type> - Add subscription")
    print("  remove_sub <username> - Remove subscription")
    print("  exit - Exit console")
    print("="*50)

def list_users():
    """List all users."""
    db = get_db()
    if not db:
        print("❌ Database not available")
        return
    
    try:
        users = db.query(User).all()
        print(f"\n📋 Total users: {len(users)}")
        print("-" * 60)
        
        for user in users[:10]:  # Show first 10 users
            sub_info = f" ({user.subscription_type})" if user.subscription_type else " (no subscription)"
            print(f"👤 {user.first_name} @{user.username}{sub_info}")
        
        if len(users) > 10:
            print(f"... and {len(users) - 10} more users")
            
        db.close()
    except Exception as e:
        logger.error(f"Error listing users: {e}")
        print(f"❌ Error: {e}")
        if db:
            db.close()

def show_stats():
    """Show bot statistics."""
    db = get_db()
    if not db:
        print("❌ Database not available")
        return
    
    try:
        total_users = db.query(User).count()
        active_subs = db.query(User).filter(User.subscription_type.isnot(None)).count()
        
        print(f"\n📊 SPEAKYZ Bot Statistics")
        print("-" * 30)
        print(f"👥 Total users: {total_users}")
        print(f"💰 Active subscriptions: {active_subs}")
        print(f"📈 Subscription rate: {(active_subs/total_users*100):.1f}%" if total_users > 0 else "📈 Subscription rate: 0%")
        
        db.close()
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        print(f"❌ Error: {e}")
        if db:
            db.close()

def add_subscription(username, sub_type):
    """Add subscription to user."""
    valid_types = ['start', 'smart', 'pro_plus', 'speaking_club']
    if sub_type not in valid_types:
        print(f"❌ Invalid subscription type. Valid types: {', '.join(valid_types)}")
        return
    
    db = get_db()
    if not db:
        print("❌ Database not available")
        return
    
    try:
        user = db.query(User).filter(User.username == username.replace('@', '')).first()
        if not user:
            print(f"❌ User @{username} not found")
            db.close()
            return
        
        user.subscription_type = sub_type
        user.subscription_end = datetime.utcnow() + timedelta(days=30)
        user.updated_at = datetime.utcnow()
        
        db.commit()
        db.close()
        
        print(f"✅ Added {sub_type} subscription to @{username}")
        
    except Exception as e:
        logger.error(f"Error adding subscription: {e}")
        print(f"❌ Error: {e}")
        if db:
            db.close()

def remove_subscription(username):
    """Remove subscription from user."""
    db = get_db()
    if not db:
        print("❌ Database not available")
        return
    
    try:
        user = db.query(User).filter(User.username == username.replace('@', '')).first()
        if not user:
            print(f"❌ User @{username} not found")
            db.close()
            return
        
        user.subscription_type = None
        user.subscription_end = None
        user.speaking_clubs_count = 0
        user.updated_at = datetime.utcnow()
        
        db.commit()
        db.close()
        
        print(f"✅ Removed subscription from @{username}")
        
    except Exception as e:
        logger.error(f"Error removing subscription: {e}")
        print(f"❌ Error: {e}")
        if db:
            db.close()

def process_console_command(command):
    """Process console command."""
    parts = command.strip().split()
    if not parts:
        return True
    
    cmd = parts[0].lower()
    
    if cmd == 'help':
        console_help()
    elif cmd == 'users':
        list_users()
    elif cmd == 'stats':
        show_stats()
    elif cmd == 'add_sub':
        if len(parts) >= 3:
            add_subscription(parts[1], parts[2])
        else:
            print("Usage: add_sub <username> <subscription_type>")
    elif cmd == 'remove_sub':
        if len(parts) >= 2:
            remove_subscription(parts[1])
        else:
            print("Usage: remove_sub <username>")
    elif cmd in ['exit', 'quit']:
        print("👋 Exiting admin console...")
        return False
    else:
        print(f"❌ Unknown command: {cmd}. Type 'help' for available commands.")
    
    return True

def console_loop():
    """Main console loop."""
    print("🔧 SPEAKYZ Admin Console started")
    print("Type 'help' for available commands")
    
    while True:
        try:
            command = input("\nspeakyz-admin> ")
            if not process_console_command(command):
                break
        except (EOFError, KeyboardInterrupt):
            print("\n👋 Exiting admin console...")
            break
        except Exception as e:
            logger.error(f"Console error: {e}")
            print(f"❌ Console error: {e}")

def start_console_admin():
    """Start console admin in a separate thread."""
    try:
        # Run console in a separate thread
        console_thread = threading.Thread(target=console_loop, daemon=True)
        console_thread.start()
        logger.info("Console admin started")
    except Exception as e:
        logger.error(f"Failed to start console admin: {e}")
