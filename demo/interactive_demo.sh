#!/bin/bash

# Interactive demo script for the help system
# This script shows how to test the help features manually

echo "🎯 Ollama CLI Help System Demo"
echo "================================"
echo ""

echo "1. Testing command-line help:"
echo "   python ../ollama_cli.py --help"
echo ""
echo "Press Enter to run..."
read -r
python ../ollama_cli.py --help

echo ""
echo "2. Testing the help system programmatically:"
echo "   python help_system_demo.py"
echo ""
echo "Press Enter to run..."
read -r
python help_system_demo.py

echo ""
echo "3. Interactive CLI Demo:"
echo "   To test interactively, run: python ../ollama_cli.py"
echo "   Then try these commands:"
echo "   - /help"
echo "   - /help search"
echo "   - /help examples"
echo "   - /help tips"
echo "   - /help nonexistent"
echo "   - /exit"
echo ""
echo "🎉 Demo complete! Run the above commands to test interactively."
