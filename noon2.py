import asyncio
import os
import random
import logging
from typing import Optional

import aiohttp
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.types import BusinessConnection
from aiogram.methods.set_business_account_name import SetBusinessAccountName

load_dotenv()

class Config:
    API_TOKEN = os.getenv("BOT_TOKEN")
    BASE_NICK = os.getenv("BASE_NICK", "noon")
    MIN_INTERVAL = 2.0
    MAX_INTERVAL = 15.0
    INTERVAL_STEP = 0.2
    
    if not API_TOKEN:
        raise RuntimeError("Переменная окружения BOT_TOKEN не установлена")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

class NickGenerator:
    UNICODE_REPLACEMENTS = {
        'a': ['а', 'α', 'ą', 'ä', 'à', 'á', 'â', 'ã', 'å', 'ā', '∆', '▲'],
        'e': ['е', 'ε', 'ę', 'ë', 'è', 'é', 'ê', 'ē', '€', '∑'],
        'o': ['о', 'ο', 'ö', 'ò', 'ó', 'ô', 'õ', 'ø', 'ō', '○', '●', '◯', '⭕'],
        'i': ['і', 'ι', 'ï', 'ì', 'í', 'î', 'ī', '!', '|', '¡'],
        'u': ['υ', 'ü', 'ù', 'ú', 'û', 'ū', 'µ'],
        'n': ['и', 'ν', 'ñ', 'ń', 'ň', 'η'],
        's': ['ѕ', 'σ', 'ś', 'š', 'ş', '$'],
        't': ['т', 'τ', 'ţ', 'ť', '†'],
        'r': ['г', 'ρ', 'ř', 'ŕ'],
        'p': ['р', 'π', 'þ'],
        'c': ['с', 'ç', 'ć', 'č', '©'],
        'h': ['н', 'η', 'ħ'],
        'x': ['х', 'χ', '×', '✗', '✘'],
        'b': ['в', 'β', 'ъ'],
        'k': ['κ', 'ķ'],
        'y': ['у', 'ψ', 'ý', 'ÿ'],
        'm': ['м', 'μ'],
        'l': ['ł', 'λ', '|'],
        'w': ['ω', 'ẅ'],
        'd': ['δ', 'đ'],
        'f': ['φ', 'ƒ'],
        'g': ['γ', 'ğ'],
        'j': ['ј'],
        'q': ['θ'],
        'v': ['ν'],
        'z': ['ζ', 'ž', 'ź', 'ż'],
    }
    
    DECORATORS = [
        ('✧', '✧'), ('♦', '♦'), ('▲', '▲'), ('♡', '♡'), ('☆', '☆'), ('★', '★'),
        ('⚡', '⚡'), ('💥', '💥'), ('🔥', '🔥'), ('⭐', '⭐'), ('🌟', '🌟'),
        ('✨', '✨'), ('💫', '💫'), ('🔸', '🔸'), ('🔷', '🔷'), ('▣', '▣'),
        ('▢', '▢'), ('▦', '▦'), ('▧', '▧'), ('▨', '▨'), ('▩', '▩'),
        ('☾', '☽'), ('🌙', '🌙'), ('◉', '◉'), ('●', '●'), ('▪', '▪'),
        ('◇', '◇'), ('♤', '♤'), ('☯', '☯'), ('❖', '❖'), ('◆', '◆'),
    ]
    
    FONT_STYLES = {
        'bold': {
            'a': '𝗮', 'b': '𝗯', 'c': '𝗰', 'd': '𝗱', 'e': '𝗲', 'f': '𝗳', 'g': '𝗴',
            'h': '𝗵', 'i': '𝗶', 'j': '𝗷', 'k': '𝗸', 'l': '𝗹', 'm': '𝗺', 'n': '𝗻',
            'o': '𝗼', 'p': '𝗽', 'q': '𝗾', 'r': '𝗿', 's': '𝘀', 't': '𝘁', 'u': '𝘂',
            'v': '𝘃', 'w': '𝘄', 'x': '𝘅', 'y': '𝘆', 'z': '𝘇'
        },
        'italic': {
            'a': '𝒂', 'b': '𝒃', 'c': '𝒄', 'd': '𝒅', 'e': '𝒆', 'f': '𝒇', 'g': '𝒈',
            'h': '𝒉', 'i': '𝒊', 'j': '𝒋', 'k': '𝒌', 'l': '𝒍', 'm': '𝒎', 'n': '𝒏',
            'o': '𝒐', 'p': '𝒑', 'q': '𝒒', 'r': '𝒓', 's': '𝒔', 't': '𝒕', 'u': '𝒖',
            'v': '𝒗', 'w': '𝒘', 'x': '𝒙', 'y': '𝒚', 'z': '𝒛'
        },
        'script': {
            'a': '𝓪', 'b': '𝓫', 'c': '𝓬', 'd': '𝓭', 'e': '𝓮', 'f': '𝓯', 'g': '𝓰',
            'h': '𝓱', 'i': '𝓲', 'j': '𝓳', 'k': '𝓴', 'l': '𝓵', 'm': '𝓶', 'n': '𝓷',
            'o': '𝓸', 'p': '𝓹', 'q': '𝓺', 'r': '𝓻', 's': '𝓼', 't': '𝓽', 'u': '𝓾',
            'v': '𝓿', 'w': '𝔀', 'x': '𝔁', 'y': '𝔂', 'z': '𝔃'
        },
        'double': {
            'a': '𝕒', 'b': '𝕓', 'c': '𝕔', 'd': '𝕕', 'e': '𝕖', 'f': '𝕗', 'g': '𝕘',
            'h': '𝕙', 'i': '𝕚', 'j': '𝕛', 'k': '𝕜', 'l': '𝕝', 'm': '𝕞', 'n': '𝕟',
            'o': '𝕠', 'p': '𝕡', 'q': '𝕢', 'r': '𝕣', 's': '𝕤', 't': '𝕥', 'u': '𝕦',
            'v': '𝕧', 'w': '𝕨', 'x': '𝕩', 'y': '𝕪', 'z': '𝕫'
        },
        'fullwidth': {
            'a': 'ａ', 'b': 'ｂ', 'c': 'ｃ', 'd': 'ｄ', 'e': 'ｅ', 'f': 'ｆ', 'g': 'ｇ',
            'h': 'ｈ', 'i': 'ｉ', 'j': 'ｊ', 'k': 'ｋ', 'l': 'ｌ', 'm': 'ｍ', 'n': 'ｎ',
            'o': 'ｏ', 'p': 'ｐ', 'q': 'ｑ', 'r': 'ｒ', 's': 'ｓ', 't': 'ｔ', 'u': 'ｕ',
            'v': 'ｖ', 'w': 'ｗ', 'x': 'ｘ', 'y': 'ｙ', 'z': 'ｚ'
        }
    }
    
    @classmethod
    def generate_variants(cls, base_nick: str, count: int = 50) -> list[str]:
        base_nick = base_nick.lower()
        variants = [base_nick]
        
        for _ in range(count - 1):
            variant_type = random.choice(['unicode', 'decorated', 'styled', 'mixed', 'spaced'])
            
            if variant_type == 'unicode':
                variant = cls._apply_unicode_replacements(base_nick)
            elif variant_type == 'decorated':
                variant = cls._apply_decorators(base_nick)
            elif variant_type == 'styled':
                variant = cls._apply_font_style(base_nick)
            elif variant_type == 'mixed':
                variant = cls._apply_mixed_style(base_nick)
            else:
                variant = cls._apply_spaced_style(base_nick)
            
            if variant and variant not in variants:
                variants.append(variant)
        
        return variants
    
    @classmethod
    def _apply_unicode_replacements(cls, nick: str) -> str:
        result = ""
        for char in nick:
            if char.lower() in cls.UNICODE_REPLACEMENTS:
                replacement = random.choice(cls.UNICODE_REPLACEMENTS[char.lower()])
                result += replacement
            else:
                result += char
        return result
    
    @classmethod
    def _apply_decorators(cls, nick: str) -> str:
        left, right = random.choice(cls.DECORATORS)
        return f"{left}{nick}{right}"
    
    @classmethod
    def _apply_font_style(cls, nick: str) -> str:
        style = random.choice(list(cls.FONT_STYLES.keys()))
        font_map = cls.FONT_STYLES[style]
        
        result = ""
        for char in nick:
            if char.lower() in font_map:
                result += font_map[char.lower()]
            else:
                result += char
        return result
    
    @classmethod
    def _apply_mixed_style(cls, nick: str) -> str:
        base = cls._apply_unicode_replacements(nick)
        if random.choice([True, False]):
            base = cls._apply_decorators(base)
        return base
    
    @classmethod
    def _apply_spaced_style(cls, nick: str) -> str:
        spacers = ['⚡', '✦', '●', '○', '◇', '♦', '▪', '▫', '◦', '•']
        spacer = random.choice(spacers)
        
        if len(nick) <= 2:
            return f"{spacer}{nick}{spacer}"
        
        result = spacer
        for i, char in enumerate(nick):
            result += char
            if i < len(nick) - 1:
                result += spacer
        result += spacer
        
        return result

class NameChanger:
    def __init__(self, bot: Bot):
        self.bot = bot
        self.business_connection_id: Optional[str] = None
        self.name_change_task: Optional[asyncio.Task] = None
        self.current_interval = Config.MIN_INTERVAL
        self.nick_variants = NickGenerator.generate_variants(Config.BASE_NICK, 100)
        logger.info(f"Сгенерировано {len(self.nick_variants)} вариантов для '{Config.BASE_NICK}'")
    
    def is_rate_limit_error(self, error_text: str) -> bool:
        rate_limit_keywords = ["too many requests", "rate limit", "flood", "429", "retry after"]
        return any(keyword in str(error_text).lower() for keyword in rate_limit_keywords)
    
    def increase_interval(self) -> None:
        if self.current_interval < Config.MAX_INTERVAL:
            old_interval = self.current_interval
            self.current_interval = min(self.current_interval + Config.INTERVAL_STEP, Config.MAX_INTERVAL)
            logger.info(f"📈 Увеличиваю интервал с {old_interval:.1f}с до {self.current_interval:.1f}с")
    
    def reset_interval(self) -> None:
        self.current_interval = Config.MIN_INTERVAL
        logger.info(f"🔄 Интервал сброшен до {self.current_interval:.1f}с")
    
    async def set_business_name_direct(self, nick: str) -> dict:
        url = f"https://api.telegram.org/bot{Config.API_TOKEN}/setBusinessAccountName"
        payload = {
            "business_connection_id": self.business_connection_id,
            "first_name": nick,
            "name": nick
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as response:
                result = await response.json()
                logger.info(f"🌐 Прямой API ответ: {result}")
                return result
    
    async def try_change_name(self, nick: str) -> bool:
        try:
            result = await self.bot(SetBusinessAccountName(
                business_connection_id=self.business_connection_id,
                name=nick,
                first_name=nick
            ))
            
            if result:
                logger.info("✅ Успешно изменено через aiogram")
                return True
                
        except Exception as api_e:
            if self.is_rate_limit_error(str(api_e)):
                logger.warning(f"⛔ Rate limit через aiogram: {api_e}")
                self.increase_interval()
            else:
                logger.error(f"❌ Ошибка aiogram: {api_e}")
            
            try:
                direct_result = await self.set_business_name_direct(nick)
                
                if direct_result.get('ok'):
                    logger.info("✅ Успешно через прямой API")
                    return True
                elif self.is_rate_limit_error(str(direct_result)):
                    logger.warning("⛔ Rate limit и через прямой API")
                    self.increase_interval()
                else:
                    logger.error(f"❌ Ошибка прямого API: {direct_result}")
                    
            except Exception as direct_e:
                if self.is_rate_limit_error(str(direct_e)):
                    logger.warning("⛔ Rate limit прямой API exception")
                    self.increase_interval()
                else:
                    logger.error(f"❌ Exception прямого API: {direct_e}")
        
        return False
    
    async def change_name_loop(self) -> None:
        logger.info(f"Запущен цикл смены имени для базового ника: '{Config.BASE_NICK}'")
        logger.info(f"Прогрессивная система: {Config.MIN_INTERVAL}с → {Config.MAX_INTERVAL}с")
        
        change_count = 0
        
        while True:
            try:
                if not self.business_connection_id:
                    logger.warning("ID бизнес-подключения не найден")
                    await asyncio.sleep(self.current_interval)
                    continue
                
                nick = random.choice(self.nick_variants)
                change_count += 1
                
                logger.info(f"🔄 [{change_count}] Меняю на: '{nick}' | Интервал: {self.current_interval:.1f}с")
                
                success = await self.try_change_name(nick)
                
                if success:
                    self.increase_interval()
                    
            except Exception as e:
                logger.error(f"❌ Общая ошибка: {e}")
            
            progress = (self.current_interval - Config.MIN_INTERVAL) / (Config.MAX_INTERVAL - Config.MIN_INTERVAL) * 100
            logger.info(f"⏰ Жду {self.current_interval:.1f}с... (прогресс: {progress:.1f}%)")
            await asyncio.sleep(self.current_interval)
    
    def start_task(self) -> None:
        if self.name_change_task and not self.name_change_task.done():
            self.name_change_task.cancel()
        
        self.reset_interval()
        self.name_change_task = asyncio.create_task(self.change_name_loop())
        logger.info("Запущена задача смены имени")
    
    def stop_task(self) -> None:
        if self.name_change_task and not self.name_change_task.done():
            self.name_change_task.cancel()
            logger.info("Задача смены имени остановлена")
    
    async def shutdown(self) -> None:
        logger.info("Завершение работы...")
        self.stop_task()
        
        if self.name_change_task:
            try:
                await self.name_change_task
            except asyncio.CancelledError:
                pass

bot = Bot(token=Config.API_TOKEN)
dp = Dispatcher()
name_changer = NameChanger(bot)

@dp.business_connection()
async def handle_business_connection(connection: BusinessConnection):
    name_changer.business_connection_id = connection.id
    logger.info(f"Подключение бизнес-аккаунта: {connection.id}")
    logger.info(f"Пользователь: {connection.user.first_name} (@{connection.user.username})")
    logger.info(f"Статус подключения: {connection.is_enabled}")
    
    if connection.is_enabled:
        name_changer.start_task()
    else:
        logger.warning("Бизнес-подключение не активно")
        name_changer.stop_task()

async def main():
    logger.info("🚀 Запуск бота...")
    logger.info(f"Bot token: {Config.API_TOKEN[:10]}...")
    logger.info(f"Базовый ник: '{Config.BASE_NICK}'")
    logger.info(f"Прогрессивная система смены: {Config.MIN_INTERVAL}с → {Config.MAX_INTERVAL}с")
    
    try:
        bot_info = await bot.get_me()
        logger.info(f"Бот запущен: @{bot_info.username}")
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
    finally:
        await name_changer.shutdown()
        await bot.session.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот остановлен пользователем")
    except Exception as e:
        logger.error(f"Неожиданная ошибка: {e}")