# Subh Paper Worker Leave Portal - Android APK

यह mobile app employee को internet के जरिए leave application Firebase में भेजने और अपना latest status देखने देता है। Existing Factory desktop app उसी Firebase path को पढ़ता है, इसलिए office को application मिल सकती है।

## APK बनाने का आसान तरीका: GitHub Actions

1. इस पूरे folder को GitHub repository में upload करें।
2. `.github/workflows/build-apk.yml` workflow चलाएँ।
3. Workflow complete होने के बाद `Artifacts` में `subhpaper-worker-leave-apk` डाउनलोड करें।
4. Android phone में APK install करें।

## जरूरी Firebase setting

अभी app आपके existing Firebase Realtime Database URL का उपयोग करता है:
`https://factoryleaveapp-default-rtdb.firebaseio.com/applications`

यह simple version existing system के साथ compatibility के लिए बनाया गया है। Production में Firebase Authentication और Security Rules लगाना जरूरी है, क्योंकि केवल Employee Code पर status access सुरक्षित नहीं है।

## Existing desktop app

आपका existing `app_gui.PY` इसी `applications` path से mobile applications लेता है और status को `Approved`/`Rejected` में update करता है।
