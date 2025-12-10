const { createApp, ref, computed, onMounted } = Vue;

createApp({
    setup() {
        const currentTab = ref('dashboard');
        const invoices = ref([]);
        const selectedInvoice = ref(null);
        const dragActive = ref(false);
        const fileInput = ref(null);
        const validationResult = ref(null);

        const API_BASE = '/api';

        // Stats
        const todaysCount = computed(() => {
            const today = new Date().toISOString().split('T')[0];
            return invoices.value.filter(i => i.uploaded_at?.startsWith(today)).length;
        });

        const pendingReviewCount = computed(() =>
            invoices.value.filter(i => ['extracted', 'needs_review'].includes(i.status)).length
        );

        const completedCount = computed(() =>
            invoices.value.filter(i => i.status === 'completed').length
        );

        // Actions
        const fetchInvoices = async () => {
            try {
                const res = await fetch(`${API_BASE}/invoices?size=100`);
                const data = await res.json();
                invoices.value = data.invoices;
            } catch (e) {
                console.error("Failed to fetch invoices", e);
            }
        };

        const uploadFile = async (file) => {
            if (!file || file.type !== 'application/pdf') {
                alert("Please upload a PDF file.");
                return;
            }

            const formData = new FormData();
            formData.append('file', file);

            try {
                const res = await fetch(`${API_BASE}/invoices/upload`, {
                    method: 'POST',
                    body: formData
                });

                if (res.ok) {
                    await fetchInvoices();
                    // Optionally select it immediately
                } else {
                    alert("Upload failed.");
                }
            } catch (e) {
                alert("Error uploading file: " + e.message);
            }
        };

        const processInvoice = async (id) => {
            try {
                // Optimistic update
                const inv = invoices.value.find(i => i.id === id);
                if (inv) inv.status = 'processing';

                await fetch(`${API_BASE}/invoices/${id}/process`, { method: 'POST' });
                // We should poll here or wait, but simpler for now implies background
                setTimeout(fetchInvoices, 2000);
            } catch (e) {
                alert("Process failed: " + e.message);
            }
        };

        const validateInvoice = async (id) => {
            try {
                const res = await fetch(`${API_BASE}/invoices/${id}/validate`, { method: 'POST' });
                const result = await res.json();
                validationResult.value = result;
                // Refresh data to show status update
                await fetchInvoices();
            } catch (e) {
                console.error(e);
            }
        }

        const handleDrop = (e) => {
            dragActive.value = false;
            const files = e.dataTransfer.files;
            if (files.length) uploadFile(files[0]);
        };

        const handleFileSelect = (e) => {
            if (e.target.files.length) uploadFile(e.target.files[0]);
        };

        const selectInvoice = (inv) => {
            selectedInvoice.value = inv;
            validationResult.value = null; // Reset validation view
        };

        const statusClass = (status) => {
            const map = {
                'uploaded': 'bg-gray-100 text-gray-600 border-gray-200',
                'processing': 'bg-blue-50 text-blue-600 border-blue-100',
                'extracted': 'bg-purple-50 text-purple-600 border-purple-100',
                'validated': 'bg-green-50 text-green-600 border-green-100',
                'needs_review': 'bg-orange-50 text-orange-600 border-orange-100',
                'completed': 'bg-teal-50 text-teal-600 border-teal-100',
                'failed': 'bg-red-50 text-red-600 border-red-100',
            };
            return map[status] || map['uploaded'];
        };

        const formatStatus = (status) => {
            return status ? status.replace('_', ' ').toUpperCase() : 'UNKNOWN';
        };

        const formatCurrency = (val) => {
            if (!val) return '0 ₫';
            return new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(val);
        };

        onMounted(() => {
            fetchInvoices();
            setInterval(fetchInvoices, 10000); // Poll every 10s
        });

        return {
            currentTab,
            invoices,
            selectedInvoice,
            dragActive,
            fileInput,
            todaysCount,
            pendingReviewCount,
            completedCount,
            handleDrop,
            handleFileSelect,
            fetchInvoices,
            selectInvoice,
            statusClass,
            formatStatus,
            formatCurrency,
            processInvoice,
            validateInvoice,
            validationResult
        };
    }
}).mount('#app');
