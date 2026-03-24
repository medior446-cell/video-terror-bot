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

def generate_horror_image(prompt):
    """Genera imagen de terror con Flux Schnell (gratis en Replicate)"""
    if not REPLICATE_API_KEY:
        return None, "⚠️ Replicate API no configurada"
    
    try:
        # Mejorar el prompt para hacerlo más terrorífico
        enhanced_prompt = f"dark horror scene, {prompt}, creepy atmosphere, cinematic lighting, highly detailed, scary, ominous, terrifying, nightmare fuel, photorealistic horror"
        
        output = replicate.run(
            "black-forest-labs/flux-schnell",
            input={
                "prompt": enhanced_prompt,
                "num_outputs": 1,
                "aspect_ratio": "16:9",
                "output_format": "jpg",
                "output_quality": 90
            }
        )
        
        # Replicate devuelve una lista de URLs
        if output and len(output) > 0:
            return output[0], None
        return None, "No se pudo generar la imagen"
        
    except Exception as e:
        logging.error(f"Error generando imagen: {str(e)}")
        return None, f"⚠️ Error: {str(e)}"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /start"""
    welcome_msg = (
        "🎬 *GENERADOR DE VIDEOS DE TERROR* 🎬\n\n"
        "Envíame una descripción y crearé una imagen de terror cinematográfica.\n\n"
        "📹 *Comandos:*\n"
        "/video [descripción] - Genera imagen de terror\n\n"
        "Ejemplo: /video una casa abandonada en el bosque de noche"
    )
    await update.message.reply_text(welcome_msg, parse_mode='Markdown')

async def video_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Genera imagen de terror"""
    if not context.args:
        await update.message.reply_text("❌ Debes proporcionar una descripción. Ejemplo:\n/video casa embrujada")
        return
    
    prompt = ' '.join(context.args)
    
    await update.message.reply_text(f"🎬 Generando imagen de terror: *{prompt}*...", parse_mode='Markdown')
    
    image_url, error = generate_horror_image(prompt)
    
    if error:
        await update.message.reply_text(error)
        return
    
    if image_url:
        await update.message.reply_text("✅ Imagen generada! Enviando...")
        await update.message.reply_photo(photo=image_url, caption=f"🕯️ {prompt}")
    else:
        await update.message.reply_text("❌ No se pudo generar la imagen")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Maneja mensajes de texto libre"""
    user_text = update.message.text
    
    await update.message.reply_text("🎬 Generando imagen de terror...", parse_mode='Markdown')Add bot_video.py - Generador de imágenes de terror con Flux
    
    image_url, error = generate_horror_image(user_text)
    
    if error:
        await update.message.reply_text(error)
        return
    
    if image_url:
        await update.message.reply_photo(photo=image_url, caption=f"🕯️ {user_text}")
    else:
        await update.message.reply_text("❌ No se pudo generar la imagen")

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
