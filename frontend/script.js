/* TaskFlow — Frontend Logic
   - Uses Fetch API to talk to the real backend
   - Renders task list via document.createElement / appendChild (no innerHTML for user data)
   - Caches task list in localStorage; renders from cache first while live data loads
   - Add, edit, delete interactions with addEventListener (no inline onclick)
   - Client-side validation on the add-task form
*/

const API_BASE = "http://127.0.0.1:8000";
const CACHE_KEY = "taskflow_tasks_cache";
const PROJECT_CACHE_KEY = "taskflow_projects_cache";

let currentProjectId = null;
let currentTasks = [];

// ---------------------------------------------------------------------------
// DOM helpers
// ---------------------------------------------------------------------------

const el = (id) => document.getElementById(id);

function showToast(message, type = "") {
    const toast = el("toast");
    toast.textContent = message;
    toast.className = "toast show " + type;
    setTimeout(() => {
        toast.className = "toast " + type;
    }, 2500);
}

// ---------------------------------------------------------------------------
// localStorage cache
// ---------------------------------------------------------------------------

function cacheTasks(tasks) {
    localStorage.setItem(CACHE_KEY, JSON.stringify(tasks));
}

function getCachedTasks() {
    try {
        const raw = localStorage.getItem(CACHE_KEY);
        return raw ? JSON.parse(raw) : [];
    } catch (e) {
        return [];
    }
}

function cacheProjects(projects) {
    localStorage.setItem(PROJECT_CACHE_KEY, JSON.stringify(projects));
}

function getCachedProjects() {
    try {
        const raw = localStorage.getItem(PROJECT_CACHE_KEY);
        return raw ? JSON.parse(raw) : [];
    } catch (e) {
        return [];
    }
}

// ---------------------------------------------------------------------------
// Projects
// ---------------------------------------------------------------------------

async function loadProjects() {
    // Render from cache first
    const cached = getCachedProjects();
    if (cached.length > 0) {
        populateProjectSelect(cached);
    }

    try {
        const res = await fetch(`${API_BASE}/projects`);
        if (!res.ok) throw new Error("Failed to load projects");
        const projects = await res.json();
        cacheProjects(projects);
        populateProjectSelect(projects);
    } catch (e) {
        console.error("Error loading projects:", e);
    }
}

function populateProjectSelect(projects) {
    const select = el("project-select");
    select.innerHTML = "";

    if (projects.length === 0) {
        const opt = document.createElement("option");
        opt.value = "";
        opt.textContent = "No projects yet";
        select.appendChild(opt);
        return;
    }

    const placeholder = document.createElement("option");
    placeholder.value = "";
    placeholder.textContent = "All Projects";
    select.appendChild(placeholder);

    projects.forEach((p) => {
        const opt = document.createElement("option");
        opt.value = String(p.id);
        opt.textContent = p.name;
        select.appendChild(opt);
    });
}

// ---------------------------------------------------------------------------
// Tasks — fetch, render, cache
// ---------------------------------------------------------------------------

async function loadTasks() {
    // Render from cache first so the page never shows a blank list
    const cached = getCachedTasks();
    if (cached.length > 0) {
        currentTasks = cached;
        renderTaskList(cached);
        updateTaskCount(cached.length);
    }

    try {
        let url = `${API_BASE}/tasks`;
        const sortSelect = el("sort-select");
        const sortVal = sortSelect.value;
        if (sortVal) {
            url += `?sort=${sortVal}`;
        }

        const res = await fetch(url);
        if (!res.ok) throw new Error("Failed to load tasks");
        const tasks = await res.json();
        currentTasks = tasks;
        cacheTasks(tasks);
        renderTaskList(tasks);
        updateTaskCount(tasks.length);
    } catch (e) {
        console.error("Error loading tasks:", e);
        if (cached.length === 0) {
            el("task-list").innerHTML = "";
            const msg = document.createElement("div");
            msg.className = "empty-msg";
            msg.textContent = "Could not connect to backend. Make sure the server is running on " + API_BASE;
            el("task-list").appendChild(msg);
        }
    }
}

function renderTaskList(tasks) {
    const container = el("task-list");
    container.innerHTML = "";

    if (!tasks || tasks.length === 0) {
        const msg = document.createElement("div");
        msg.className = "empty-msg";
        msg.textContent = "No tasks yet. Add one using the form on the left.";
        container.appendChild(msg);
        return;
    }

    // Filter by selected project if one is selected
    let displayTasks = tasks;
    if (currentProjectId) {
        displayTasks = tasks.filter((t) => String(t.project_id) === String(currentProjectId));
    }

    if (displayTasks.length === 0) {
        const msg = document.createElement("div");
        msg.className = "empty-msg";
        msg.textContent = "No tasks in this project yet.";
        container.appendChild(msg);
        return;
    }

    displayTasks.forEach((task) => {
        container.appendChild(createTaskElement(task));
    });
}

function createTaskElement(task) {
    const item = document.createElement("div");
    item.className = "task-item";
    item.dataset.taskId = String(task.id);

    // Task info section
    const info = document.createElement("div");
    info.className = "task-info";

    const title = document.createElement("div");
    title.className = "task-title";
    title.textContent = task.title; // textContent for user-provided text
    info.appendChild(title);

    const meta = document.createElement("div");
    meta.className = "task-meta";

    // Priority tag
    const priorityTag = document.createElement("span");
    priorityTag.className = `tag tag-priority-${task.priority}`;
    priorityTag.textContent = task.priority;
    meta.appendChild(priorityTag);

    // Status tag
    const statusTag = document.createElement("span");
    statusTag.className = `tag tag-status-${task.status}`;
    statusTag.textContent = task.status.replace("_", " ");
    meta.appendChild(statusTag);

    // Due date tag (if present)
    if (task.due_date) {
        const dueTag = document.createElement("span");
        dueTag.className = "tag tag-due";
        dueTag.textContent = "Due: " + task.due_date;
        meta.appendChild(dueTag);
    }

    info.appendChild(meta);
    item.appendChild(info);

    // Action buttons
    const actions = document.createElement("div");
    actions.className = "task-actions";

    const editBtn = document.createElement("button");
    editBtn.className = "action-btn edit-btn";
    editBtn.textContent = "Edit";
    editBtn.addEventListener("click", () => openEditModal(task));

    const deleteBtn = document.createElement("button");
    deleteBtn.className = "action-btn delete-btn";
    deleteBtn.textContent = "Delete";
    deleteBtn.addEventListener("click", () => deleteTask(task.id));

    actions.appendChild(editBtn);
    actions.appendChild(deleteBtn);
    item.appendChild(actions);

    return item;
}

function updateTaskCount(count) {
    el("task-count-badge").textContent = `${count} task${count !== 1 ? "s" : ""}`;
}

// ---------------------------------------------------------------------------
// Stats
// ---------------------------------------------------------------------------

async function loadStats() {
    if (!currentProjectId) {
        el("stat-total").textContent = "0";
        el("stat-pending").textContent = "0";
        el("stat-in-progress").textContent = "0";
        el("stat-done").textContent = "0";
        return;
    }

    try {
        const res = await fetch(`${API_BASE}/projects/${currentProjectId}/stats`);
        if (!res.ok) return;
        const stats = await res.json();
        el("stat-total").textContent = String(stats.total_tasks);
        el("stat-pending").textContent = String(stats.pending);
        el("stat-in-progress").textContent = String(stats.in_progress);
        el("stat-done").textContent = String(stats.done);
    } catch (e) {
        console.error("Error loading stats:", e);
    }
}

// ---------------------------------------------------------------------------
// Add task
// ---------------------------------------------------------------------------

function validateAddForm() {
    const titleInput = el("task-title");
    const errorEl = el("title-error");
    const trimmed = titleInput.value.trim();

    if (!trimmed) {
        errorEl.textContent = "Title is required";
        titleInput.classList.add("input-error");
        return false;
    } else {
        errorEl.textContent = "";
        titleInput.classList.remove("input-error");
        return true;
    }
}

async function handleAddTask(event) {
    event.preventDefault();

    if (!validateAddForm()) {
        return;
    }

    const title = el("task-title").value.trim();
    const priority = el("task-priority").value;
    const dueDate = el("task-due-date").value.trim() || null;
    const projectId = currentProjectId || el("project-select").value;

    if (!projectId) {
        showToast("Please select a project first", "error");
        return;
    }

    try {
        const res = await fetch(`${API_BASE}/tasks`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                title: title,
                priority: priority,
                status: "pending",
                due_date: dueDate,
                project_id: parseInt(projectId),
            }),
        });

        if (!res.ok) {
            const err = await res.json();
            throw new Error(err.detail || "Failed to create task");
        }

        const newTask = await res.json();
        el("task-title").value = "";
        el("task-due-date").value = "";
        el("title-error").textContent = "";

        await loadTasks();
        await loadStats();
        showToast("Task added", "success");
    } catch (e) {
        showToast(e.message, "error");
    }
}

// ---------------------------------------------------------------------------
// Quick-add (AI parser)
// ---------------------------------------------------------------------------

async function handleQuickAdd(event) {
    event.preventDefault();

    const desc = el("quick-add-desc").value.trim();
    const errorEl = el("quick-add-error");

    if (!desc) {
        errorEl.textContent = "Description is required";
        return;
    }
    errorEl.textContent = "";

    const projectId = currentProjectId || el("project-select").value;
    if (!projectId) {
        showToast("Please select a project first", "error");
        return;
    }

    try {
        const res = await fetch(`${API_BASE}/tasks/quick-add`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                description: desc,
                project_id: parseInt(projectId),
            }),
        });

        if (!res.ok) {
            const err = await res.json();
            throw new Error(err.detail || "Failed to quick-add task");
        }

        el("quick-add-desc").value = "";
        await loadTasks();
        await loadStats();
        showToast("Task created via AI Quick-Add", "success");
    } catch (e) {
        showToast(e.message, "error");
    }
}

// ---------------------------------------------------------------------------
// Edit task (modal)
// ---------------------------------------------------------------------------

function openEditModal(task) {
    el("edit-task-id").value = String(task.id);
    el("edit-title").value = task.title;
    el("edit-priority").value = task.priority;
    el("edit-status").value = task.status;
    el("edit-due-date").value = task.due_date || "";
    el("edit-title-error").textContent = "";
    el("edit-modal").classList.add("show");
}

function closeEditModal() {
    el("edit-modal").classList.remove("show");
}

async function handleEditTask(event) {
    event.preventDefault();

    const taskId = parseInt(el("edit-task-id").value);
    const title = el("edit-title").value.trim();
    const errorEl = el("edit-title-error");

    if (!title) {
        errorEl.textContent = "Title is required";
        return;
    }
    errorEl.textContent = "";

    const updateData = {
        title: title,
        priority: el("edit-priority").value,
        status: el("edit-status").value,
        due_date: el("edit-due-date").value.trim() || null,
    };

    try {
        const res = await fetch(`${API_BASE}/tasks/${taskId}`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(updateData),
        });

        if (!res.ok) {
            const err = await res.json();
            throw new Error(err.detail || "Failed to update task");
        }

        closeEditModal();
        await loadTasks();
        await loadStats();
        showToast("Task updated", "success");
    } catch (e) {
        showToast(e.message, "error");
    }
}

// ---------------------------------------------------------------------------
// Delete task
// ---------------------------------------------------------------------------

async function deleteTask(taskId) {
    if (!confirm("Are you sure you want to delete this task?")) {
        return;
    }

    try {
        const res = await fetch(`${API_BASE}/tasks/${taskId}`, {
            method: "DELETE",
        });

        if (!res.ok && res.status !== 204) {
            throw new Error("Failed to delete task");
        }

        await loadTasks();
        await loadStats();
        showToast("Task deleted", "success");
    } catch (e) {
        showToast(e.message, "error");
    }
}

// ---------------------------------------------------------------------------
// Event listeners and initialization
// ---------------------------------------------------------------------------

document.addEventListener("DOMContentLoaded", () => {
    // Load projects and tasks
    loadProjects();
    loadTasks();

    // Add task form submit
    el("add-task-form").addEventListener("submit", handleAddTask);

    // Quick-add form submit
    el("quick-add-form").addEventListener("submit", handleQuickAdd);

    // Title validation — remove error as user types
    el("task-title").addEventListener("input", () => {
        if (el("task-title").value.trim()) {
            el("title-error").textContent = "";
            el("task-title").classList.remove("input-error");
        }
    });

    // Project select change
    el("project-select").addEventListener("change", (e) => {
        currentProjectId = e.target.value || null;
        renderTaskList(currentTasks);
        loadStats();
    });

    // Sort select change
    el("sort-select").addEventListener("change", () => {
        loadTasks();
    });

    // Edit modal
    el("edit-task-form").addEventListener("submit", handleEditTask);
    el("edit-cancel").addEventListener("click", closeEditModal);
    el("edit-modal").addEventListener("click", (e) => {
        if (e.target === el("edit-modal")) {
            closeEditModal();
        }
    });
});
