#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI Commit — автоматически генерирует сообщение коммита по изменениям в коде.
Требует установленный и запущенный ollama (локально).
"""

import subprocess
import sys
import argparse

# Модель по умолчанию (вы уже скачали qwen2.5-coder:7b)
DEFAULT_MODEL = "qwen2.5-coder:7b"


def get_git_diff():
    """Возвращает diff текущих изменений (сначала staged, потом unstaged)."""
    try:
        # Пытаемся получить diff для staged
        diff = subprocess.check_output(
            ["git", "diff", "--cached", "--no-color"],
            stderr=subprocess.DEVNULL,
            text=True,
            encoding="utf-8"
        )
        if not diff.strip():
            # Если нет staged, берём unstaged
            diff = subprocess.check_output(
                ["git", "diff", "--no-color"],
                stderr=subprocess.DEVNULL,
                text=True,
                encoding="utf-8"
            )
        return diff
    except subprocess.CalledProcessError as e:
        print("❌ Не удалось получить diff. Убедитесь, что вы в git-репозитории.")
        sys.exit(1)


def generate_commit_message(diff, model):
    """Отправляет diff модели Ollama и получает сообщение коммита."""
    prompt = (
        "Ты — эксперт по Git. Напиши краткое сообщение коммита (одной строкой) в стиле Conventional Commits, "
        "которое описывает следующие изменения в коде. Не добавляй лишних комментариев, только само сообщение.\n\n"
        f"Изменения:\n{diff}"
    )

    try:
        import ollama
        response = ollama.chat(
            model=model,
            messages=[{"role": "user", "content": prompt}]
        )
        # Извлекаем текст ответа и убираем лишние пробелы/кавычки
        msg = response['message']['content'].strip()
        # Убираем возможные обрамляющие кавычки, которые иногда добавляет модель
        if msg.startswith('"') and msg.endswith('"'):
            msg = msg[1:-1]
        return msg
    except Exception as e:
        print(f"❌ Ошибка при обращении к ollama: {e}")
        print("Проверьте, что ollama запущен (команда 'ollama serve') и модель загружена.")
        print("Если модель не скачана, выполните: ollama pull qwen2.5-coder:7b")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Генератор сообщений коммита через AI (Ollama)")
    parser.add_argument(
        "-m", "--model",
        default=DEFAULT_MODEL,
        help=f"Модель Ollama (по умолчанию: {DEFAULT_MODEL})"
    )
    args = parser.parse_args()

    diff = get_git_diff()
    if not diff.strip():
        print("⚠️ Нет изменений для коммита. Добавьте файлы через 'git add'.")
        return

    print("🤖 Генерирую сообщение коммита (модель: {})...".format(args.model))
    msg = generate_commit_message(diff, args.model)
    print("\n💡 Предлагаемое сообщение:\n")
    print(msg)
    print("\n✅ Если подходит, выполните:")
    print(f'   git commit -m "{msg}"')
    print("   Или скопируйте сообщение и отредактируйте.")


if __name__ == "__main__":
    main()