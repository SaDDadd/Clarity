#!/usr/bin/env python3
"""
AI Commit — автоматически генерирует сообщение коммита по изменениям в коде.
Требует установленный и запущенный ollama (или можно заменить на API GPT).
"""

import subprocess
import sys
import argparse
import json

# Настройки: выбери модель из ollama
MODEL = "qwen2.5-coder:7b"  # или "llama3.2", "mistral", "qwen2.5-coder"
# Если хочешь использовать OpenAI, раскомментируй и укажи ключ
# USE_OPENAI = False
# OPENAI_API_KEY = "sk-..."

def get_git_diff():
    """Возвращает diff текущих изменений"""
    try:
        diff = subprocess.check_output(
            ["git", "diff", "--cached", "--no-color"],
            stderr=subprocess.DEVNULL,
            text=True
        )
        if not diff.strip():
            # Если нет изменений в staged, берём unstaged
            diff = subprocess.check_output(
                ["git", "diff", "--no-color"],
                stderr=subprocess.DEVNULL,
                text=True
            )
        return diff
    except subprocess.CalledProcessError:
        print("❌ Не удалось получить diff. Вы в git-репозитории?")
        sys.exit(1)

def generate_commit_message(diff, use_ollama=True):
    """Отправляет diff модели и получает сообщение коммита"""
    prompt = (
        "Ты — эксперт по Git. Напиши краткое сообщение коммита (одной строкой) в стиле Conventional Commits, "
        "которое описывает следующие изменения в коде. Не добавляй лишних комментариев, только само сообщение.\n\n"
        f"Изменения:\n{diff}"
    )

    if use_ollama:
        try:
            import ollama
            response = ollama.chat(model=MODEL, messages=[{"role": "user", "content": prompt}])
            return response['message']['content'].strip()
        except Exception as e:
            print(f"❌ Ошибка при обращении к ollama: {e}")
            print("Убедитесь, что ollama запущен (ollama serve) и модель загружена.")
            sys.exit(1)
    else:
        # Вариант с OpenAI API (раскомментируй при необходимости)
        # import openai
        # openai.api_key = OPENAI_API_KEY
        # response = openai.ChatCompletion.create(
        #     model="gpt-3.5-turbo",
        #     messages=[{"role": "user", "content": prompt}],
        #     max_tokens=50
        # )
        return response.choices[0].message.content.strip()

def main():
    parser = argparse.ArgumentParser(description="Генератор сообщений коммита через AI")
    parser.add_argument("-m", "--model", default=MODEL, help="Модель ollama")
    parser.add_argument("--openai", action="store_true", help="Использовать OpenAI API вместо ollama")
    args = parser.parse_args()

    diff = get_git_diff()
    if not diff.strip():
        print("⚠️ Нет изменений для коммита. Добавьте файлы через git add.")
        return

    print("🤖 Генерирую сообщение коммита...")
    msg = generate_commit_message(diff, use_ollama=not args.openai)
    print("\n💡 Предлагаемое сообщение:\n")
    print(msg)
    print("\n✅ Если подходит, выполните:")
    print(f'   git commit -am "{msg}"')
    print("   Или скопируйте сообщение и отредактируйте.")

if __name__ == "__main__":
    main()