document.addEventListener('DOMContentLoaded', function () {
    const stepList = document.getElementById('step-list');
    let draggedItem = null;

    // ドラッグ可能な要素のイベントリスナーを設定
    function addDragListeners(item) {
        item.setAttribute('draggable', true);

        item.addEventListener('dragstart', function (e) {
            draggedItem = item;
            e.dataTransfer.effectAllowed = 'move';
            item.classList.add('dragging');
        });

        item.addEventListener('dragend', function (e) {
            draggedItem = null;
            item.classList.remove('dragging');
        });

        item.addEventListener('dragover', function (e) {
            e.preventDefault();
            const rect = item.getBoundingClientRect();
            const midY = rect.top + rect.height / 2;
            if (e.clientY < midY) {
                item.classList.add('drag-above');
                item.classList.remove('drag-below');
            } else {
                item.classList.add('drag-below');
                item.classList.remove('drag-above');
            }
        });

        item.addEventListener('dragleave', function (e) {
            item.classList.remove('drag-above', 'drag-below');
        });

        item.addEventListener('drop', function (e) {
            e.preventDefault();
            if (draggedItem === item) return;

            const items = [...stepList.children];
            const draggedIndex = items.indexOf(draggedItem);
            const droppedIndex = items.indexOf(item);

            const rect = item.getBoundingClientRect();
            const midY = rect.top + rect.height / 2;
            const insertAfter = e.clientY > midY;

            if (insertAfter) {
                item.parentNode.insertBefore(draggedItem, item.nextSibling);
            } else {
                item.parentNode.insertBefore(draggedItem, item);
            }

            item.classList.remove('drag-above', 'drag-below');

            // 順序を更新
            updateStepOrders();
        });
    }

    // ステップの順序を更新してサーバーに送信
    async function updateStepOrders() {
        const items = [...stepList.children];
        const updates = items.map((item, index) => ({
            stepId: item.dataset.stepId,
            newOrder: index + 1
        }));

        try {
            const response = await fetch('/update_step_orders', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ updates: updates })
            });

            if (!response.ok) {
                throw new Error('順序の更新に失敗しました');
            }

            // 順序の表示を更新
            items.forEach((item, index) => {
                const orderSpan = item.querySelector('.step-order');
                if (orderSpan) {
                    orderSpan.textContent = `[${index + 1}]`;
                }
            });
        } catch (error) {
            console.error('Error:', error);
            alert('順序の更新中にエラーが発生しました');
        }
    }

    // 既存のステップ要素にドラッグ機能を追加
    document.querySelectorAll('#step-list li').forEach(addDragListeners);
});