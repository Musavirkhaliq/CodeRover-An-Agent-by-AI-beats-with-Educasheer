document.addEventListener('DOMContentLoaded', () => {
    const currentDisplay = document.getElementById('current-display');
    const historyDisplay = document.getElementById('history-display');
    const buttons = document.querySelector('.buttons');
    const calculationHistoryList = document.getElementById('calculation-history');
    const clearHistoryBtn = document.getElementById('clear-history');

    let currentInput = '0';
    let operator = null;
    let previousInput = '';
    let history = [];
    let waitingForSecondOperand = false;

    // Load history from localStorage
    const loadHistory = () => {
        const storedHistory = localStorage.getItem('calculatorHistory');
        if (storedHistory) {
            history = JSON.parse(storedHistory);
            renderHistory();
        }
    };

    // Save history to localStorage
    const saveHistory = () => {
        localStorage.setItem('calculatorHistory', JSON.stringify(history));
    };

    const updateDisplay = () => {
        currentDisplay.textContent = currentInput;
        historyDisplay.textContent = previousInput + (operator ? ' ' + operator : '');
    };

    const appendNumber = (number) => {
        if (waitingForSecondOperand) {
            currentInput = number;
            waitingForSecondOperand = false;
        } else {
            currentInput = currentInput === '0' ? number : currentInput + number;
        }
        updateDisplay();
    };

    const appendDecimal = () => {
        if (waitingForSecondOperand) {
            currentInput = '0.';
            waitingForSecondOperand = false;
        } else if (!currentInput.includes('.')) {
            currentInput += '.';
        }
        updateDisplay();
    };

    const handleOperator = (nextOperator) => {
        const inputValue = parseFloat(currentInput);

        if (operator && waitingForSecondOperand) {
            operator = nextOperator;
            historyDisplay.textContent = previousInput + ' ' + operator;
            return;
        }

        if (previousInput === '') {
            previousInput = inputValue;
        } else if (operator) {
            const calculation = performCalculation[operator](parseFloat(previousInput), inputValue);
            const expression = `${previousInput} ${operator} ${currentInput} = ${calculation}`;
            addToHistory(expression, calculation);
            currentInput = String(calculation);
            previousInput = calculation;
        }

        waitingForSecondOperand = true;
        operator = nextOperator;
        updateDisplay();
    };

    const performCalculation = {
        '/': (firstOperand, secondOperand) => secondOperand !== 0 ? firstOperand / secondOperand : 'Error',
        '*': (firstOperand, secondOperand) => firstOperand * secondOperand,
        '+': (firstOperand, secondOperand) => firstOperand + secondOperand,
        '-': (firstOperand, secondOperand) => firstOperand - secondOperand,
    };

    const calculateResult = () => {
        if (!operator || waitingForSecondOperand) return;

        const inputValue = parseFloat(currentInput);
        const calculation = performCalculation[operator](parseFloat(previousInput), inputValue);

        const expression = `${previousInput} ${operator} ${currentInput} = ${calculation}`;
        addToHistory(expression, calculation);
        
        currentInput = String(calculation);
        operator = null;
        previousInput = '';
        waitingForSecondOperand = false;
        updateDisplay();
    };

    const clearCalculator = () => {
        currentInput = '0';
        operator = null;
        previousInput = '';
        waitingForSecondOperand = false;
        updateDisplay();
    };

    const toggleNegative = () => {
        currentInput = String(parseFloat(currentInput) * -1);
        updateDisplay();
    };

    const calculatePercentage = () => {
        currentInput = String(parseFloat(currentInput) / 100);
        updateDisplay();
    };

    const addToHistory = (expression, result) => {
        history.unshift({ expression, result: String(result) });
        if (history.length > 10) { // Keep history limited to 10 items
            history.pop();
        }
        saveHistory();
        renderHistory();
    };

    const renderHistory = () => {
        calculationHistoryList.innerHTML = '';
        if (history.length === 0) {
            calculationHistoryList.innerHTML = '<li style="text-align: center; color: #888;">No history yet.</li>';
            return;
        }
        history.forEach(item => {
            const li = document.createElement('li');
            li.innerHTML = `<span class="expression">${item.expression.split('=').map(s => s.trim())[0]}</span><span class="result">= ${item.result}</span>`;
            calculationHistoryList.appendChild(li);
        });
    };

    const clearAllHistory = () => {
        history = [];
        saveHistory();
        renderHistory();
    };

    buttons.addEventListener('click', (event) => {
        const { target } = event;
        if (!target.matches('button')) {
            return;
        }

        if (target.classList.contains('number')) {
            appendNumber(target.textContent);
        } else if (target.classList.contains('operator')) {
            const action = target.dataset.action;
            switch (action) {
                case 'add':
                case 'subtract':
                case 'multiply':
                case 'divide':
                    handleOperator(target.textContent);
                    break;
                case 'negative':
                    toggleNegative();
                    break;
                case 'percent':
                    calculatePercentage();
                    break;
            }
        } else if (target.classList.contains('decimal')) {
            appendDecimal();
        } else if (target.classList.contains('clear')) {
            clearCalculator();
        } else if (target.classList.contains('equals')) {
            calculateResult();
        }
    });

    clearHistoryBtn.addEventListener('click', clearAllHistory);

    // Initial load
    loadHistory();
    updateDisplay();
});