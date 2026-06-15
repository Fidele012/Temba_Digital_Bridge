/**
 * Temba Digital Bridge — AI Assistant Widget
 * Rule-based chatbot with professional escalation for water & sanitation queries
 * Self-contained: injects HTML/CSS into any page automatically
 */

(function () {
  'use strict';

  // ─── Knowledge Base ─────────────────────────────────────────────────────────
  const KB = [
    {
      id: 'greeting',
      keywords: ['hello','hi','hey','good morning','good afternoon','good evening',
                 'muraho','mwaramutse','amakuru','help','start','assist','what can you do'],
      response: `Hello! I'm **Temba Assistant** — your digital guide for water and sanitation services in Rwanda.\n\nI can help you with:\n\n• **Reporting** water or sanitation issues\n• **Tracking** your submitted reports\n• **Booking** appointments with service providers\n• **Requesting** water services (connections, tanks, trucks)\n• **Water safety** information\n• **Navigating** the Temba platform\n\nWhat would you like help with today?`,
      professional: false,
      quickReplies: ['How do I report an issue?','Book an appointment','Check report status','Water safety info']
    },
    {
      id: 'report_how',
      keywords: ['report','submit','file','send','raise','create report','new report','make report','how report'],
      response: `**How to Report a Water Issue:**\n\n**Step 1:** Click **"Report Issue"** in the navigation menu\n**Step 2:** Select the issue category (broken pipe, no water, contamination…)\n**Step 3:** Choose your location — Province → District → Sector → Cell → Village\n**Step 4:** Select your water service provider\n**Step 5:** Write a description and attach photos if available\n**Step 6:** Click Submit — you'll get a reference number (e.g. #TDB-1234)\n\n**No internet?** Dial **\*XXX#** on any phone to report via USSD in English or Kinyarwanda.\n\nYour report goes directly to the provider who will review and respond.`,
      professional: false,
      quickReplies: ['What types of issues can I report?','How do I track my report?','Report via USSD']
    },
    {
      id: 'report_track',
      keywords: ['track','status','check','update','progress','follow up','my report',
                 'reference','ref number','tdb','what happened','no update','pending'],
      response: `**Tracking Your Reports:**\n\n1. Open your **Dashboard** and click **"My Reports"** in the sidebar\n2. Your reports show colour-coded status badges:\n   • 🔵 **Submitted** — received, awaiting review\n   • 🟠 **In Progress** — provider is working on it\n   • 🟢 **Resolved** — issue has been fixed\n3. Click any report card to view full details and provider notes\n4. You'll also receive **SMS alerts** whenever your report status changes\n\n**Via USSD:** Dial **\*XXX#** → select "Check Status" → enter your reference number`,
      professional: false,
      quickReplies: ['My report has no update','How long does resolution take?','Contact my provider']
    },
    {
      id: 'report_types',
      keywords: ['categories','types of issue','what issues','what can report','broken pipe','leak',
                 'no water','dry tap','shortage','low pressure','flooding','sewage','sanitation','pump'],
      response: `**Issues You Can Report on Temba:**\n\n🔴 **Urgent**\n• Broken or burst pipes\n• Water contamination (bad smell/colour/taste)\n• Complete water outage\n• Sewage overflow or flooding\n\n🟠 **Moderate**\n• Low water pressure\n• Intermittent or dry taps\n• Damaged public taps or pumps\n• Broken water meters\n\n🔵 **Standard**\n• Poor water quality (general)\n• Infrastructure damage (non-emergency)\n• Drainage problems\n• Meter reading disputes\n\nEvery report helps providers identify patterns and prioritise repairs in your area.`,
      professional: false,
      quickReplies: ['How do I report contamination?','Submit a report now','What is considered urgent?']
    },
    {
      id: 'contamination',
      keywords: ['contaminated','contamination','chemical','bad smell','smell bad','color','colour',
                 'brown water','black water','yellow water','smell sewage','unsafe water','polluted',
                 'dirty water','oily','strange taste','weird taste'],
      response: `⚠️ **Suspected Water Contamination — Act Immediately:**\n\n**Right now:**\n1. **Stop drinking** the water\n2. Use bottled or stored clean water for drinking and cooking\n3. **Submit an URGENT report** on Temba — select "Contamination" category\n4. Warn your neighbours\n\n**If anyone is already ill from the water**, go to the nearest health centre immediately.\n\nWater contamination is a **public health matter** that requires urgent professional investigation. I'll help you connect with the right specialist.`,
      professional: true,
      professionalMsg: 'Water contamination can affect an entire community and requires urgent assessment by a certified water quality specialist and possibly public health authorities.',
      quickReplies: ['Submit urgent report','Contact WASAC','Find nearest health centre']
    },
    {
      id: 'health_medical',
      keywords: ['sick','ill','disease','hospital','doctor','health','diarrhea','diarrhoea',
                 'vomiting','stomach ache','stomach pain','fever','rash','allergic',
                 'poisoned','poisoning','medical','unwell','hurting'],
      response: `🏥 **Health Issues Possibly Linked to Water:**\n\nIf you or someone is experiencing health symptoms that may be related to water quality:\n\n1. **Seek immediate medical care** at your nearest health centre or hospital\n2. **Stop drinking** tap water until the source is confirmed safe\n3. **Report suspected contamination** on Temba so providers can investigate\n4. Keep a record of symptoms and when they started\n\n**Rwanda Emergency:** Call **912**\n**Nearest health centre:** Visit your local Umudugudu leader for directions\n\nThis is a medical situation — please prioritise getting professional healthcare.`,
      professional: true,
      professionalMsg: 'Health symptoms potentially caused by water require both medical attention and a water quality investigation by certified professionals.',
      quickReplies: ['Emergency: Call 912','Report contamination now','Submit urgent report']
    },
    {
      id: 'appointment_book',
      keywords: ['appointment','book','schedule','meeting','consultation','visit','meet provider',
                 'talk to provider','discuss','call back','callback','see provider'],
      response: `**Booking an Appointment with a Provider:**\n\n1. Go to your **Dashboard** → click **"Appointments"** in the sidebar\n2. Click **"Book Appointment"**\n3. Select your **water service provider** (filtered by your service area)\n4. Choose the **reason** (new connection, billing, meter, general inquiry…)\n5. Pick your **preferred date and available time slot**\n6. Add notes and click Submit\n\n**After booking:**\n• The provider reviews and approves within 1–2 business days\n• You'll receive an SMS/email confirmation or a proposed alternative time\n• You can **reschedule or cancel** at any time from your dashboard\n\nAppointments are free — you pay nothing to book.`,
      professional: false,
      quickReplies: ['Can I reschedule an appointment?','Can I cancel?','View my appointments']
    },
    {
      id: 'appointment_reschedule',
      keywords: ['reschedule','change time','change date','postpone','move appointment',
                 'different time','not available','change appointment','update appointment'],
      response: `**Rescheduling an Appointment:**\n\n1. Open **Dashboard** → **Appointments**\n2. Find the appointment you want to change\n3. Click **"Reschedule"** on that appointment\n4. Choose a new preferred date and time\n5. Add a note explaining the change (optional)\n6. Submit — the provider will be notified and confirm\n\n**Notes:**\n• You can reschedule any **Pending** or **Approved** appointment\n• Appointments with status **"Completed"** or **"Rejected"** cannot be changed\n• The provider may propose yet another alternative time if your choice is unavailable`,
      professional: false,
      quickReplies: ['How to cancel instead?','View my appointments','Book a new appointment']
    },
    {
      id: 'appointment_cancel',
      keywords: ['cancel appointment','cancel booking','delete appointment','remove appointment',
                 'no longer need','cancel meeting','withdraw appointment'],
      response: `**Cancelling an Appointment:**\n\n1. Go to **Dashboard** → **Appointments**\n2. Find the appointment you want to cancel\n3. Click **"Cancel"** and select a reason\n4. Confirm the cancellation\n\nThe provider will be automatically notified.\n\n**Important:**\n• Please cancel **at least 24 hours in advance** where possible — this helps providers manage their schedules\n• You can book a new appointment at any time after cancellation\n• Frequent cancellations may affect your ability to book priority slots`,
      professional: false,
      quickReplies: ['Book a new appointment','Reschedule instead','View my appointments']
    },
    {
      id: 'service_request',
      keywords: ['service request','request service','request water','apply for water',
                 'water connection','pipe installation','new connection','connect water',
                 'water tank','tank delivery','water truck','truck delivery','emergency water',
                 'meter install','meter repair','inspection','technical visit','borehole'],
      response: `**Requesting Water Services on Temba:**\n\nYou can request any of these services from registered providers:\n\n💧 **New Water Connection** — pipe installation to your home/property\n🚰 **Tank Delivery** — water storage tank supplied and installed\n🚛 **Water Truck** — emergency bulk water delivery to your location\n📊 **Meter Support** — installation, repair, or incorrect readings\n🔧 **Technical Inspection** — infrastructure assessment visit\n\n**How to request:**\n1. Go to **Dashboard** → **Service Requests**\n2. Click **"New Request"**\n3. Choose the service type and provider\n4. Enter your exact location and requirements\n5. Submit — provider reviews and responds within 2–5 business days`,
      professional: false,
      quickReplies: ['Request water connection','Request water truck','Check request status']
    },
    {
      id: 'water_connection',
      keywords: ['new connection','connect my house','water to home','pipe to house',
                 'household connection','water line','extend pipeline','home water','apply connection'],
      response: `**Applying for a New Home Water Connection:**\n\n**What you need ready:**\n• Full name and phone number\n• Exact property location (Province to Village)\n• Type of property (residential, commercial, rental…)\n• Any land/property documents if available\n\n**The process:**\n1. Submit a **Connection Request** in Dashboard → Service Requests\n2. Provider reviews feasibility for your area\n3. A site inspection is scheduled (provider will call you)\n4. You receive a cost quote\n5. Connection is installed after approval\n\n**Typical timeline:** 2–4 weeks after approval\n**Cost:** Varies by provider and distance to the nearest main pipe — the provider will quote after inspection.`,
      professional: false,
      quickReplies: ['Which provider for connections?','Submit connection request now','How long does it take?']
    },
    {
      id: 'water_truck',
      keywords: ['water truck','truck delivery','emergency delivery','bulk water','no water emergency',
                 'drought','run out of water','urgent water supply','fill tank'],
      response: `**Requesting Emergency Water Truck Delivery:**\n\nThis service is for situations like:\n• Extended water outage in your area\n• Drought or infrastructure failure\n• Community or event needs\n\n**How to request:**\n1. Go to **Dashboard** → **Service Requests** → **"New Request"**\n2. Select **"Water Truck Delivery"** as the service type\n3. Set urgency to **High** if it's an emergency\n4. Enter your exact delivery location and quantity needed\n5. Submit\n\n**For immediate emergencies, call directly:**\n• **WASAC:** +250 788 123 456\n• **Water Access Rwanda:** +250 788 234 567\n\nDon't wait for online processing in a true emergency — call first.`,
      professional: false,
      quickReplies: ['Submit truck request now','Contact WASAC directly','Which providers offer trucks?']
    },
    {
      id: 'providers_info',
      keywords: ['provider','wasac','water access','iriba','aquasan','pro water',
                 'water company','utility','service company','contact provider','who covers'],
      response: `**Registered Water Service Providers on Temba:**\n\n🏢 **WASAC** — National coverage, water supply & sanitation\n📞 +250 788 123 456 | info@wasac.rw\n\n🏢 **Water Access Rwanda** — Rural water supply\n📞 +250 788 234 567 | contact@wateraccessrwanda.rw\n\n🏢 **IRIBA Water Group** — Urban & peri-urban distribution\n📞 +250 788 345 678 | support@iriba.rw\n\n🏢 **Aquasan Limited** — Sanitation services (Kigali)\n📞 +250 788 456 789 | info@aquasan.rw\n\n🏢 **Pro Water Rwanda** — Commercial water services\n📞 +250 788 567 890 | hello@prowater.rw\n\nVisit **Dashboard → Providers** for full contact details and to book appointments directly.`,
      professional: false,
      quickReplies: ['Book appointment with provider','Report issue to provider','Which provider covers my area?']
    },
    {
      id: 'ussd',
      keywords: ['ussd','dial','basic phone','no smartphone','no internet','feature phone',
                 'offline','without internet','star code','*xxx#','kinyarwanda phone'],
      response: `**Using Temba via USSD (No Internet Required):**\n\nDial **\*XXX#** on **any phone** — basic phone, smartphone, or even a borrowed phone.\n\n**USSD Main Menu:**\n1. Report Water Issue\n2. Request Water Service\n3. Check Request Status\n4. Announcements & Alerts\n5. Request Callback from Provider\n6. Exit\n\n**Available in:**\n• 🇷🇼 Kinyarwanda\n• 🇬🇧 English\n\n**What you can do via USSD:**\n• Report any water or sanitation issue\n• Request water services (truck, connection, meter support)\n• Check status by reference number\n• Receive emergency announcements\n• Request a provider to call you back\n\n**Tip:** USSD sessions time out quickly — read each prompt and respond within 30 seconds.`,
      professional: false,
      quickReplies: ['How to report via USSD?','What is my reference number?','How to check status via USSD?']
    },
    {
      id: 'account_signup',
      keywords: ['register','sign up','create account','join','new account','membership',
                 'how to register','make account','open account'],
      response: `**Creating a Temba Account:**\n\n**Community Member (free, instant):**\n1. Click **"Sign Up"** on the homepage\n2. Select **"Community Member"**\n3. Enter personal info — name, phone, ID\n4. Set your residential location (Province to Village)\n5. Create a password\n6. Your account is **active immediately** — start reporting!\n\n**Water Service Provider (verified):**\n1. Click **"Sign Up"** → **"Water Provider"**\n2. Enter organisation details and select your service categories\n3. Specify the provinces/districts you operate in\n4. Submit for admin verification\n5. Account activated within **1–2 business days** after review\n\n[Sign Up Now →](signup.html)`,
      professional: false,
      quickReplies: ['Sign up as community member','Register as provider','I already have an account']
    },
    {
      id: 'account_password',
      keywords: ['password','forgot','reset','login','sign in','cannot log in','locked out',
                 'access account','forgot password','change password'],
      response: `**Account Access & Password Help:**\n\n**Forgot your password?**\n1. Go to the **Sign In** page\n2. Click **"Forgot password?"**\n3. Enter your registered phone number or email\n4. You'll receive a reset code via SMS or email\n5. Create a new password\n\n**Still stuck?**\n• Make sure you're using the phone number or email you registered with\n• Check you're not switching between community and provider login tabs\n• Try a different browser or clear your cache\n\n**Alternative:** Use USSD **\*XXX#** to request a callback from your provider's support team.\n\n[Go to Sign In →](signin.html)`,
      professional: false,
      quickReplies: ['Go to sign in','Sign up instead','Need more help']
    },
    {
      id: 'billing_dispute',
      keywords: ['bill','billing','invoice','charge','payment','overcharged','wrong amount',
                 'dispute','fee','cost','price','expensive bill','meter reading wrong',
                 'incorrect reading'],
      response: `**Billing Inquiries & Disputes:**\n\nBilling matters require your full account history and records — these are best handled by a provider's billing officer directly.\n\n**Steps to resolve:**\n1. **Book an appointment** with your provider (Dashboard → Appointments) — select "Billing Dispute" as the reason\n2. **Call the provider** billing line for urgent issues\n3. **Request a meter inspection** if you believe your readings are incorrect (Dashboard → Service Requests)\n\nBring any bills or receipts you have to the appointment.\n\nI'll connect you with the right professional for this.`,
      professional: true,
      professionalMsg: 'Billing disputes involve your personal account records and financial data. A qualified billing officer at your water service provider is the right person to resolve this.',
      quickReplies: ['Book appointment','Request meter inspection','Contact provider directly']
    },
    {
      id: 'major_infrastructure',
      keywords: ['main pipe burst','road flooding','major leak','burst main','large crack',
                 'infrastructure collapse','emergency repair','big flood','massive leak',
                 'street flooding','road damaged'],
      response: `⚠️ **Major Infrastructure Emergency:**\n\n**Immediate actions:**\n1. **Stay away** from the damaged area\n2. **Call WASAC** directly for emergency response: **+250 788 123 456**\n3. Submit an **Urgent report** on Temba (select highest urgency)\n4. Alert your local authority (sector office) if the damage affects roads or public property\n\n**This situation requires emergency-response infrastructure engineers** — please call the provider directly and don't wait for online processing.`,
      professional: true,
      professionalMsg: 'Major infrastructure damage needs immediate response from certified water engineers and emergency teams — online processing alone is not fast enough.',
      quickReplies: ['Call WASAC emergency','Submit urgent report','Contact local authority']
    },
    {
      id: 'water_safety',
      keywords: ['safe to drink','water safety','water quality','boil water','filter water',
                 'purify water','ph level','chlorine','turbidity','e coli','bacteria','safe'],
      response: `**Water Safety Information:**\n\n**Signs your water may be unsafe:**\n• Unusual smell (chlorine, sulfur/egg, sewage)\n• Discolouration (brown, yellow, black, cloudy)\n• Unusual or bitter taste\n• Visible particles or sediment\n\n**Rwanda safe water standards:**\n• pH: 6.5–8.5 (normal range)\n• Turbidity: below 1 NTU (visually clear)\n• Chlorine: 0.2–0.5 mg/L (disinfection)\n• E. coli: 0 detected (bacteria-free)\n\n**If you're unsure:**\n1. Boil water for 1 minute before drinking\n2. Let it cool in a covered clean container\n3. Use a certified filter if available\n4. Check **Dashboard → Water Quality** for your area's current readings\n\nSuspect contamination? **Submit an urgent report immediately.**`,
      professional: false,
      quickReplies: ['Report suspected contamination','Check water quality data','Water is discoloured']
    },
    {
      id: 'about_platform',
      keywords: ['about temba','what is temba','who made temba','temba mission','purpose',
                 'goal','platform info','about this','about platform','organisation behind'],
      response: `**About Temba Digital Bridge:**\n\nTemba Digital Bridge is a **civic digital platform** built to close the communication gap between Rwandan communities and water service providers.\n\n**Our Mission:**\nEnable every Rwandan — whether online or on a basic phone — to report water issues, request services, and communicate transparently with providers.\n\n**What Temba provides:**\n• 🌐 Web application (this platform)\n• 📱 USSD (*XXX#) — no internet required\n• 📨 SMS notifications in English & Kinyarwanda\n\n**Registered Providers:**\nWASAC, Water Access Rwanda, IRIBA Water Group, Aquasan Limited, Pro Water Rwanda\n\n**Coverage:** All 5 administrative levels across Rwanda's provinces\n\n**Languages:** English and Kinyarwanda`,
      professional: false,
      quickReplies: ['How do I use Temba?','Register on Temba','View all providers']
    },
    {
      id: 'legal_regulatory',
      keywords: ['legal','law','court','lawyer','sue','rura','regulator','ministry',
                 'government complaint','regulatory','rights','legal action'],
      response: `**Legal & Regulatory Matters:**\n\nFor formal regulatory complaints or legal matters involving water services, these require specialists beyond Temba's direct scope.\n\n**Relevant contacts:**\n• **RURA** (Rwanda Utilities Regulatory Authority) — official complaints about service providers\n• **Ministry of Infrastructure** — policy-level concerns\n• **Your provider's legal/compliance department** — contractual disputes\n\n**To start a formal complaint process:**\n1. Document everything — dates, reference numbers, communications\n2. Book a formal appointment with your provider through Temba\n3. If unresolved, escalate to RURA\n\nI'll help you connect with the right professional.`,
      professional: true,
      professionalMsg: 'Legal and regulatory matters require qualified professionals. Start with a formal appointment through Temba, then escalate to RURA if needed.',
      quickReplies: ['Book formal appointment','Contact RURA','Document my issue']
    },
    {
      id: 'not_understood',
      keywords: [],
      response: `I didn't quite understand that — let me offer some topics I can help with:\n\n• **Reporting** — submit or track a water issue\n• **Appointments** — book, reschedule, or cancel\n• **Service requests** — water connections, tanks, trucks, meter support\n• **Providers** — contacts, services, coverage areas\n• **USSD access** — use Temba without internet\n• **Account help** — sign up, login, password reset\n• **Water safety** — quality standards and contamination guidance\n\nCould you rephrase your question? Or tap one of the options above.`,
      professional: false,
      quickReplies: ['Report an issue','Book appointment','Request a service','Water safety']
    }
  ];

  // ─── Scoring engine ──────────────────────────────────────────────────────────
  function findBestMatch(input) {
    const lower = input.toLowerCase().trim();
    const words = lower.split(/\W+/).filter(w => w.length > 2);
    let bestScore = 0;
    let bestTopic = null;

    for (const topic of KB) {
      if (topic.id === 'not_understood') continue;
      let score = 0;
      for (const kw of topic.keywords) {
        if (lower.includes(kw)) {
          score += kw.split(' ').length * 4; // phrase match scores high
        } else {
          for (const word of words) {
            if (kw === word) score += 3;
            else if (kw.includes(word) && word.length > 3) score += 1;
          }
        }
      }
      if (score > bestScore) { bestScore = score; bestTopic = topic; }
    }

    return bestScore >= 2 ? bestTopic : KB.find(t => t.id === 'not_understood');
  }

  // ─── Simple markdown renderer ────────────────────────────────────────────────
  function renderMd(text) {
    return text
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_self" style="color:#29B6F6;text-decoration:underline;">$1</a>')
      .replace(/\n/g, '<br>');
  }

  // ─── Message history ─────────────────────────────────────────────────────────
  const history = [];
  let isOpen = false;
  let isMinimized = false;
  let unreadCount = 0;

  // ─── Inject CSS ──────────────────────────────────────────────────────────────
  const style = document.createElement('style');
  style.textContent = `
    #temba-chat-fab {
      position: fixed; bottom: 28px; right: 28px; z-index: 9000;
      width: 56px; height: 56px; border-radius: 50%;
      background: linear-gradient(135deg, #1565C0, #29B6F6);
      border: none; cursor: pointer; display: flex; align-items: center; justify-content: center;
      box-shadow: 0 4px 20px rgba(21,101,192,0.45);
      transition: transform 0.25s, box-shadow 0.25s;
      font-size: 22px; color: #fff;
    }
    #temba-chat-fab:hover { transform: scale(1.1); box-shadow: 0 6px 28px rgba(21,101,192,0.55); }
    #temba-chat-badge {
      position: absolute; top: -4px; right: -4px;
      background: #C62828; color: #fff;
      font-size: 11px; font-weight: 700;
      width: 20px; height: 20px; border-radius: 50%;
      display: flex; align-items: center; justify-content: center;
      border: 2px solid #fff; display: none;
    }
    #temba-chat-panel {
      position: fixed; bottom: 96px; right: 28px; z-index: 8999;
      width: 360px; max-height: 560px;
      background: #fff; border-radius: 18px;
      box-shadow: 0 8px 40px rgba(10,37,64,0.18);
      display: flex; flex-direction: column;
      transform: translateY(20px) scale(0.96);
      opacity: 0; pointer-events: none;
      transition: transform 0.3s cubic-bezier(0.34,1.56,0.64,1), opacity 0.25s;
      overflow: hidden;
      font-family: 'Plus Jakarta Sans', sans-serif;
    }
    #temba-chat-panel.open {
      transform: translateY(0) scale(1); opacity: 1; pointer-events: all;
    }
    .tchat-header {
      background: linear-gradient(135deg, #0A2540, #1565C0);
      padding: 14px 16px; display: flex; align-items: center; gap: 10px;
      flex-shrink: 0;
    }
    .tchat-avatar {
      width: 36px; height: 36px; border-radius: 50%;
      background: rgba(255,255,255,0.2);
      display: flex; align-items: center; justify-content: center;
      font-size: 18px; color: #fff; flex-shrink: 0;
    }
    .tchat-header-info { flex: 1; }
    .tchat-title { font-size: 14px; font-weight: 700; color: #fff; }
    .tchat-subtitle { font-size: 11.5px; color: rgba(255,255,255,0.75); }
    .tchat-online { width: 8px; height: 8px; border-radius: 50%; background: #4CAF50; display: inline-block; margin-right: 4px; }
    .tchat-header-btn {
      background: none; border: none; color: rgba(255,255,255,0.8);
      font-size: 18px; cursor: pointer; padding: 4px; border-radius: 6px;
      transition: background 0.15s;
    }
    .tchat-header-btn:hover { background: rgba(255,255,255,0.15); color: #fff; }
    .tchat-messages {
      flex: 1; overflow-y: auto; padding: 14px 14px 8px;
      display: flex; flex-direction: column; gap: 10px;
      scroll-behavior: smooth;
    }
    .tchat-messages::-webkit-scrollbar { width: 4px; }
    .tchat-messages::-webkit-scrollbar-thumb { background: #E2E8F0; border-radius: 4px; }
    .tchat-msg { display: flex; gap: 8px; align-items: flex-end; }
    .tchat-msg.user { flex-direction: row-reverse; }
    .tchat-bubble {
      max-width: 82%; padding: 10px 13px; border-radius: 14px;
      font-size: 13px; line-height: 1.55; word-break: break-word;
    }
    .tchat-msg.bot .tchat-bubble {
      background: #F0F4F8; color: #1E293B;
      border-bottom-left-radius: 4px;
    }
    .tchat-msg.user .tchat-bubble {
      background: linear-gradient(135deg, #1565C0, #29B6F6);
      color: #fff; border-bottom-right-radius: 4px;
    }
    .tchat-bot-icon {
      width: 28px; height: 28px; border-radius: 50%;
      background: linear-gradient(135deg, #0A2540, #1565C0);
      display: flex; align-items: center; justify-content: center;
      font-size: 13px; color: #fff; flex-shrink: 0;
    }
    .tchat-msg.user .tchat-bot-icon { display: none; }
    .tchat-time { font-size: 10.5px; color: #94A3B8; margin-top: 3px; text-align: right; }
    .tchat-msg.bot .tchat-time { text-align: left; }
    .tchat-professional {
      background: #FFF8E1; border: 1.5px solid #FFD54F;
      border-radius: 10px; padding: 10px 12px; margin-top: 6px; font-size: 12px; color: #5D4037;
    }
    .tchat-professional strong { color: #E65100; }
    .tchat-connect-btn {
      display: inline-flex; align-items: center; gap: 6px;
      margin-top: 8px; padding: 7px 14px;
      background: #E65100; color: #fff; border: none; border-radius: 8px;
      font-size: 12.5px; font-weight: 600; cursor: pointer;
      transition: background 0.2s;
    }
    .tchat-connect-btn:hover { background: #BF360C; }
    .tchat-quick-replies {
      display: flex; flex-wrap: wrap; gap: 6px; margin-top: 8px;
    }
    .tchat-qr {
      background: #fff; border: 1.5px solid #1565C0; color: #1565C0;
      border-radius: 20px; padding: 5px 12px; font-size: 12px; font-weight: 600;
      cursor: pointer; transition: background 0.15s, color 0.15s;
      font-family: 'Plus Jakarta Sans', sans-serif;
    }
    .tchat-qr:hover { background: #1565C0; color: #fff; }
    .tchat-typing {
      display: flex; align-items: center; gap: 8px;
      padding: 0 14px 4px; flex-shrink: 0;
    }
    .tchat-typing-dots {
      display: flex; gap: 4px; padding: 8px 12px;
      background: #F0F4F8; border-radius: 14px; border-bottom-left-radius: 4px;
    }
    .tchat-typing-dots span {
      width: 7px; height: 7px; border-radius: 50%; background: #94A3B8;
      animation: typingBounce 1.2s infinite;
    }
    .tchat-typing-dots span:nth-child(2) { animation-delay: 0.2s; }
    .tchat-typing-dots span:nth-child(3) { animation-delay: 0.4s; }
    @keyframes typingBounce { 0%,60%,100%{transform:translateY(0)} 30%{transform:translateY(-5px)} }
    .tchat-input-row {
      display: flex; gap: 8px; padding: 10px 14px 14px;
      border-top: 1px solid #F0F4F8; flex-shrink: 0; background: #fff;
    }
    .tchat-input {
      flex: 1; padding: 9px 14px; border: 1.5px solid #E2E8F0;
      border-radius: 24px; font-size: 13px; font-family: 'Plus Jakarta Sans', sans-serif;
      outline: none; transition: border-color 0.2s; resize: none;
      color: #1E293B; background: #F8FAFB;
    }
    .tchat-input:focus { border-color: #29B6F6; background: #fff; }
    .tchat-send {
      width: 38px; height: 38px; border-radius: 50%;
      background: linear-gradient(135deg, #1565C0, #29B6F6);
      border: none; cursor: pointer; display: flex; align-items: center; justify-content: center;
      font-size: 16px; color: #fff; flex-shrink: 0;
      transition: transform 0.2s, box-shadow 0.2s;
    }
    .tchat-send:hover { transform: scale(1.1); box-shadow: 0 3px 12px rgba(21,101,192,0.4); }
    .tchat-disclaimer {
      font-size: 10.5px; color: #94A3B8; text-align: center;
      padding: 0 14px 8px; flex-shrink: 0;
    }
    @media (max-width: 440px) {
      #temba-chat-panel { width: calc(100vw - 16px); right: 8px; bottom: 80px; }
      #temba-chat-fab { right: 16px; bottom: 16px; }
    }
  `;
  document.head.appendChild(style);

  // ─── Inject HTML ─────────────────────────────────────────────────────────────
  const wrapper = document.createElement('div');
  wrapper.id = 'temba-chat-root';
  wrapper.innerHTML = `
    <!-- Chat Panel -->
    <div id="temba-chat-panel" role="dialog" aria-label="Temba Assistant">
      <div class="tchat-header">
        <div class="tchat-avatar"><i class="ti ti-robot"></i></div>
        <div class="tchat-header-info">
          <div class="tchat-title">Temba Assistant</div>
          <div class="tchat-subtitle"><span class="tchat-online"></span>Online — Water &amp; Sanitation Guide</div>
        </div>
        <button class="tchat-header-btn" onclick="tembaChat.minimize()" title="Minimize"><i class="ti ti-minus"></i></button>
        <button class="tchat-header-btn" onclick="tembaChat.close()" title="Close"><i class="ti ti-x"></i></button>
      </div>
      <div class="tchat-messages" id="tchat-messages"></div>
      <div class="tchat-typing" id="tchat-typing" style="display:none;">
        <div class="tchat-bot-icon" style="width:24px;height:24px;font-size:11px;"><i class="ti ti-robot"></i></div>
        <div class="tchat-typing-dots"><span></span><span></span><span></span></div>
      </div>
      <div class="tchat-input-row">
        <input class="tchat-input" id="tchat-input" type="text"
               placeholder="Ask about water services…" autocomplete="off"
               onkeydown="if(event.key==='Enter')tembaChat.send()">
        <button class="tchat-send" onclick="tembaChat.send()" title="Send">
          <i class="ti ti-send"></i>
        </button>
      </div>
      <div class="tchat-disclaimer">Temba AI · For emergencies call 912 or your provider directly</div>
    </div>

    <!-- FAB button -->
    <button id="temba-chat-fab" onclick="tembaChat.toggle()" title="Open Temba Assistant">
      <i class="ti ti-message-chatbot" id="temba-fab-icon"></i>
      <span id="temba-chat-badge"></span>
    </button>
  `;
  document.body.appendChild(wrapper);

  // ─── Time helper ─────────────────────────────────────────────────────────────
  function timeStr() {
    return new Date().toLocaleTimeString('en-RW', { hour: '2-digit', minute: '2-digit' });
  }

  // ─── Render message ──────────────────────────────────────────────────────────
  function appendMessage(role, content, topic) {
    const msgs = document.getElementById('tchat-messages');
    const div = document.createElement('div');
    div.className = `tchat-msg ${role}`;

    let inner = `<div class="tchat-bubble">${renderMd(content)}</div>`;

    if (role === 'bot') {
      inner = `<div class="tchat-bot-icon"><i class="ti ti-robot"></i></div>
               <div>
                 <div class="tchat-bubble">${renderMd(content)}</div>`;

      // Professional escalation box
      if (topic && topic.professional) {
        inner += `<div class="tchat-professional">
          <strong>⚡ This requires a professional</strong><br>
          ${topic.professionalMsg}
          <br>
          <button class="tchat-connect-btn" onclick="tembaChat.connectProfessional()">
            <i class="ti ti-phone-call"></i> Connect to Professional
          </button>
        </div>`;
      }

      // Quick replies
      if (topic && topic.quickReplies && topic.quickReplies.length) {
        const qr = topic.quickReplies.map(q =>
          `<button class="tchat-qr" onclick="tembaChat.quickReply('${q.replace(/'/g,"\\'")}')">
            ${q}
          </button>`
        ).join('');
        inner += `<div class="tchat-quick-replies">${qr}</div>`;
      }

      inner += `<div class="tchat-time">${timeStr()}</div></div>`;
    } else {
      inner += `<div class="tchat-time">${timeStr()}</div>`;
    }

    div.innerHTML = inner;
    msgs.appendChild(div);
    msgs.scrollTop = msgs.scrollHeight;
  }

  // ─── Typing indicator ────────────────────────────────────────────────────────
  function showTyping() {
    document.getElementById('tchat-typing').style.display = 'flex';
    const msgs = document.getElementById('tchat-messages');
    msgs.scrollTop = msgs.scrollHeight;
  }
  function hideTyping() {
    document.getElementById('tchat-typing').style.display = 'none';
  }

  // ─── Public API ──────────────────────────────────────────────────────────────
  window.tembaChat = {
    toggle() {
      isOpen ? this.close() : this.open();
    },
    open() {
      isOpen = true;
      isMinimized = false;
      document.getElementById('temba-chat-panel').classList.add('open');
      document.getElementById('temba-fab-icon').className = 'ti ti-x';
      // Clear badge
      unreadCount = 0;
      const badge = document.getElementById('temba-chat-badge');
      badge.style.display = 'none';
      // Show greeting if no history
      if (history.length === 0) {
        setTimeout(() => {
          const greeting = KB.find(t => t.id === 'greeting');
          appendMessage('bot', greeting.response, greeting);
          history.push({ role: 'bot', id: 'greeting' });
        }, 200);
      }
      setTimeout(() => document.getElementById('tchat-input').focus(), 300);
    },
    close() {
      isOpen = false;
      document.getElementById('temba-chat-panel').classList.remove('open');
      document.getElementById('temba-fab-icon').className = 'ti ti-message-chatbot';
    },
    minimize() {
      this.close();
    },
    send(overrideText) {
      const input = document.getElementById('tchat-input');
      const text = (overrideText || input.value).trim();
      if (!text) return;
      input.value = '';

      // Append user message
      appendMessage('user', text);
      history.push({ role: 'user', text });

      // Find best match & respond
      showTyping();
      const delay = 600 + Math.random() * 700;
      setTimeout(() => {
        hideTyping();
        const topic = findBestMatch(text);
        appendMessage('bot', topic.response, topic);
        history.push({ role: 'bot', id: topic.id });
        // Update unread badge if closed
        if (!isOpen) {
          unreadCount++;
          const badge = document.getElementById('temba-chat-badge');
          badge.textContent = unreadCount;
          badge.style.display = 'flex';
        }
      }, delay);
    },
    quickReply(text) {
      this.send(text);
    },
    connectProfessional() {
      const panel = document.getElementById('tchat-messages');
      const msg = `I'm connecting you with professional support options:\n\n**Immediate contacts:**\n• **WASAC Emergency:** +250 788 123 456\n• **Rwanda Emergency Services:** 912\n• **Water Access Rwanda:** +250 788 234 567\n\n**Or book a formal appointment:**\nGo to **Dashboard → Appointments** to schedule a consultation with your provider's specialist.\n\n**USSD option:** Dial **\*XXX#** → "Request Callback" — a provider will call you back.`;
      showTyping();
      setTimeout(() => {
        hideTyping();
        const connectTopic = {
          professional: false,
          quickReplies: ['Book appointment now','View providers','Call WASAC']
        };
        appendMessage('bot', msg, connectTopic);
      }, 800);
    }
  };

  // ─── Auto-show greeting bubble after page load ───────────────────────────────
  setTimeout(() => {
    if (!isOpen) {
      unreadCount = 1;
      const badge = document.getElementById('temba-chat-badge');
      badge.textContent = '1';
      badge.style.display = 'flex';
    }
  }, 4000);

}());
