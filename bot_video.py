import os
import logging
import replicate
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import requests
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Variables de entorno
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
REPLICATE_API_KEY = os.environ.get("REPLICATE_API_KEY", "")

def generate_horror_video(prompt):
    """Genera video de terror con Luma AI (hasta 5 segundos)"""
    if not REPLICATE_API_KEY:
        return None, "⚠️ Replicate API no configurada"
    
    try:
        # Mejorar el prompt para hacerlo más terrorífico
        enhanced_prompt = f"dark horror scene, {prompt}, creepy atmosphere, cinematic lighting, highly detailed, scary, ominous, terrifying, nightmare fuel"
        
        logging.info(f"Generando video de terror con Luma AI: {enhanced_prompt}")
        
        output = replicate.run(
            "lumalabs/luma-photon",
            input={
                "prompt": enhanced_prompt,
                "num_outputs": 1,
                "aspect_ratio": "16:9",
                "output_format": "mp4"
            }
        )
        
        if output and len(output) > 0:
            return output[0], None
        else:
            return None, "No se pudo generar el video"
            
    except Exception as e:
        logging.error(f"Error generando video: {str(e)}")
        return None, f"❌ Error: {str(e)}"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /start"""
    welcome_msg = (
        "🎬 *GENERADOR DE VIDEOS DE TERROR* 🎬\n\n"
        "Envíame una descripción y crearé un video de terror cinematográfico.\n\n"
        "📹 *Comandos:*\n"
        "/video [descripción] - Genera video de terror\n\n"
        "Ejemplo: /video una casa abandonada en el bosque de noche"
    )
    await update.message.reply_text(welcome_msg, parse_mode='Markdown')

async def video_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Genera video de terror"""
    if not context.args:
        await update.message.reply_text("❌ Debes proporcionar una descripción. Ejemplo:\n/video casa embrujada")
        return
    
    prompt = ' '.join(context.args)
    
    await update.message.reply_text(f"🎬 Generando video de terror: *{prompt}*... (puede tardar 1-2 minutos)", parse_mode='Markdown')
    
    video_url, error = generate_horror_video(prompt)
    
    if error:
        await update.message.reply_text(error)
        return
    
    if video_url:
        await update.message.reply_text("✅ Video generado! Enviando...")
        await update.message.reply_video(video=video_url, caption=f"🕯️ {prompt}")
    else:
        await update.message.reply_text("❌ No se pudo generar el video")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Maneja mensajes de texto libre"""
    user_text = update.message.text
    
    await update.message.reply_text("🎬 Generando video de terror... (puede tardar 1-2 minutos)", parse_mode='Markdown')
    
    video_url, error = generate_horror_video(user_text)
    
    if error:
        await update.message.reply_text(error)
        return
    
    if video_url:
        await update.message.reply_video(video=video_url, caption=f"🕯️ {user_text}")
    else:
        await update.message.reply_text("❌ No se pudo generar el video")

if __name__ == '__main__':
    if not TELEGRAM_TOKEN:
        logging.error("TELEGRAM_TOKEN no configurado")
        exit(1)
    
    if not REPLICATE_API_KEY:
        logging.warning("REPLICATE_API_KEY no configurado")
    
    logging.info("🎬 Iniciando Bot Generador de Videos de Terror...")
    
    # Configurar Replicate
    if REPLICATE_API_KEY:
        os.environ["REPLICATE_API_TOKEN"] = REPLICATE_API_KEY
    
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('video', video_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    logging.info("✅ Bot configurado. Iniciando polling...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)
