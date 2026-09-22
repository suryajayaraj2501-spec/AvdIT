// AdvIT - Razorpay & Payment Gateway Integration

async function initiatePayment({ orderType, targetId, amount, description, onSuccess, onError }) {
  try {
    const res = await fetch('/payments/create-order/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCookie('csrftoken') || ''
      },
      body: JSON.stringify({
        order_type: orderType, // 'milestone' | 'service_order'
        target_id: targetId,
        amount: amount,
        description: description
      })
    });

    const data = await res.json();
    if (!res.ok) {
      alert(data.error || "Failed to create payment order.");
      if (onError) onError(data);
      return;
    }

    // Check if Razorpay SDK is loaded
    if (typeof Razorpay !== 'undefined' && data.key_id && !data.key_id.includes('demo')) {
      const options = {
        key: data.key_id,
        amount: data.amount_in_cents,
        currency: data.currency || 'INR',
        name: "AdvIT Marketplace",
        description: description || "AdvIT Project Payment",
        order_id: data.order_id,
        handler: async function (response) {
          await verifyPaymentOnServer(response, onSuccess, onError);
        },
        prefill: {
          name: data.user_name || "",
          email: data.user_email || ""
        },
        theme: {
          color: "#4f46e5"
        }
      };
      const rzp = new Razorpay(options);
      rzp.open();
    } else {
      // Test Mode Direct Simulation Modal / Action
      showTestPaymentModal(data, onSuccess, onError);
    }
  } catch (err) {
    console.error("Payment initiation error:", err);
    alert("An error occurred initializing the payment gateway.");
  }
}

function showTestPaymentModal(orderData, onSuccess, onError) {
  let modalElem = document.getElementById('testPaymentModal');
  if (!modalElem) {
    const modalHtml = `
      <div class="modal fade" id="testPaymentModal" tabindex="-1" aria-hidden="true">
        <div class="modal-dialog modal-dialog-centered">
          <div class="modal-content border-0 shadow-lg" style="border-radius: 20px;">
            <div class="modal-header bg-dark text-white border-0 py-3" style="border-top-left-radius: 20px; border-top-right-radius: 20px;">
              <h5 class="modal-title fw-bold"><i class="bi bi-shield-lock-fill text-warning me-2"></i> Razorpay Test Checkout</h5>
              <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body p-4">
              <div class="text-center mb-4">
                <div class="display-6 fw-bold text-primary mb-1">$<span id="testModalAmount">0</span></div>
                <div class="text-muted small" id="testModalDesc">AdvIT Escrow Payment</div>
                <span class="badge bg-success mt-2">Test Mode Active</span>
              </div>
              <div class="alert alert-info py-2 small mb-4">
                <i class="bi bi-info-circle me-1"></i> Funds will be safely deposited into the AdvIT Escrow Vault.
              </div>
              <div class="d-grid gap-2">
                <button type="button" id="btnConfirmTestPay" class="btn btn-adv-primary py-2 fw-bold">
                  <i class="bi bi-check-circle-fill me-2"></i> Authorize & Fund Escrow
                </button>
                <button type="button" class="btn btn-outline-secondary py-2" data-bs-dismiss="modal">Cancel</button>
              </div>
            </div>
          </div>
        </div>
      </div>
    `;
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    modalElem = document.getElementById('testPaymentModal');
  }

  document.getElementById('testModalAmount').textContent = orderData.amount;
  document.getElementById('testModalDesc').textContent = orderData.description || 'Milestone Payment';

  const modal = new bootstrap.Modal(modalElem);
  modal.show();

  const confirmBtn = document.getElementById('btnConfirmTestPay');
  confirmBtn.onclick = async () => {
    confirmBtn.disabled = true;
    confirmBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span> Processing Escrow...';

    const testSignature = {
      razorpay_order_id: orderData.order_id,
      razorpay_payment_id: 'pay_test_' + Math.random().toString(36).substring(2, 10),
      razorpay_signature: 'sig_test_verified',
      payment_id: orderData.payment_id
    };

    await verifyPaymentOnServer(testSignature, (res) => {
      modal.hide();
      if (onSuccess) onSuccess(res);
      else window.location.reload();
    }, (err) => {
      modal.hide();
      if (onError) onError(err);
      else alert("Payment verification failed.");
    });
  };
}

async function verifyPaymentOnServer(payload, onSuccess, onError) {
  try {
    const res = await fetch('/payments/verify-signature/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCookie('csrftoken') || ''
      },
      body: JSON.stringify(payload)
    });
    const data = await res.json();
    if (res.ok) {
      if (onSuccess) onSuccess(data);
      else window.location.reload();
    } else {
      if (onError) onError(data);
      else alert(data.error || "Payment verification failed.");
    }
  } catch (e) {
    console.error("Verification error:", e);
    if (onError) onError(e);
  }
}
