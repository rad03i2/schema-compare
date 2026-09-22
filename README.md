# Schema Compare

A small, dependency-free Python CLI and library for comparing **SQLite database schemas** deterministically. It is designed for migration reviews, CI drift checks, local development, and verifying that two databases have the same structure without modifying either database.

## English

### Why it exists
Schema drift is easy to miss when databases evolve through migrations or manual changes. Schema Compare turns structural differences into a stable human-readable or JSON report and uses useful exit codes so it can gate CI jobs.

### Key features
- Opens SQLite databases in **read-only mode**.
- Compares tables and columns, including declared type, `NOT NULL`, default value, and primary-key position.
- Detects added, removed, and changed indexes, views, and triggers by their stored schema SQL.
- Deterministic ordering for review-friendly output.
- Human-readable and JSON output.
- `inspect` command for exploring one database.
- CI-friendly exit codes: `0` identical/success, `1` schema drift, `2` input/inspection error.
- Python API with no runtime dependencies beyond the standard library.
- No network access or telemetry.

### Preview
```text
$ schema-compare compare before.db after.db
Schema differences:
  Tables added: audit
  Table changed: users
    + column email (TEXT)
  - index ix_users_name
```

For a reproducible preview, run `python examples/create_demo.py` and then compare the generated databases.

### Requirements and installation
Requires Python 3.10+ and SQLite support in Python (included in normal CPython builds).

```bash
git clone https://github.com/rad03i2/schema-compare.git
cd schema-compare
python -m pip install -e .
```

### Usage
```bash
schema-compare inspect app.db
schema-compare inspect app.db --json
schema-compare compare staging.db production.db
schema-compare compare staging.db production.db --json
python -m schema_compare compare staging.db production.db
```

In CI, exit code `1` means the schemas differ. This is intentional and lets a pipeline fail on unexpected drift.

### Python API
```python
from schema_compare import compare_databases, inspect_database

schema = inspect_database("app.db")
diff = compare_databases("before.db", "after.db")
if diff["different"]:
    print(diff["tables_changed"])
```

### Configuration
There is no configuration file and no environment-variable requirement. Input paths are explicit command arguments. This keeps behavior predictable and avoids hidden credentials or network configuration.

### Project structure
```text
src/schema_compare/   core inspection/diff engine and CLI
 tests/                real SQLite unit/CLI tests
 examples/             reproducible demo database generator
 .github/workflows/    cross-platform CI
```

### Testing
```bash
python -m pip install -e . pytest
python -m compileall -q src
pytest -q
```

CI runs the suite on Python 3.10, 3.12, and 3.13 across Ubuntu, Windows, and macOS.

### Security and privacy
Databases are opened with SQLite URI `mode=ro`; the tool does not execute stored schema SQL and does not modify inputs. It makes no network requests. Schema names, defaults, and SQL definitions can themselves contain sensitive information, so protect generated reports as you would the schema. See [SECURITY.md](SECURITY.md).

### Limitations
- SQLite only; PostgreSQL/MySQL are not implemented.
- This compares structural schema metadata, not table data or migration history.
- Stored SQL text for indexes/views/triggers is compared textually, so semantically equivalent SQL with different formatting may be reported as changed.
- SQLite table options and some advanced metadata (for example complete foreign-key semantic diffing) are not yet modeled as first-class differences.
- The tool reports drift; it does not generate or execute migrations.

### Optional roadmap
Potential future additions include normalized SQL comparison, foreign-key-aware reporting, and adapters for other database engines. These are optional and not claimed as current features.

### Contributing
See [CONTRIBUTING.md](CONTRIBUTING.md). Contributions should include tests and preserve read-only behavior.

### License
MIT — see [LICENSE](LICENSE).

### Author
**Radwan Abdulhadi Ahmed**  
**رضوان عبدالهادي أحمد**  
GitHub: **@rad03i2**

---

## العربية

### نظرة عامة
**Schema Compare** أداة ومكتبة Python خفيفة لمقارنة مخططات قواعد بيانات **SQLite** بصورة حتمية وآمنة. تفيد في مراجعة الترحيلات، واكتشاف اختلاف البنية بين بيئات التطوير والإنتاج، واستخدام المقارنة كفحص داخل CI، من دون تعديل قواعد البيانات.

### لماذا هذا المشروع؟
قد يحدث اختلاف في بنية قواعد البيانات بسبب ترحيل ناقص أو تعديل يدوي. تحول الأداة هذه الاختلافات إلى تقرير واضح أو JSON، وتستخدم رموز خروج مناسبة للأتمتة حتى يمكن اكتشاف الانحراف مبكرًا.

### الميزات الرئيسية
- فتح قواعد SQLite بوضع القراءة فقط.
- مقارنة الجداول والأعمدة: النوع المعلن و`NOT NULL` والقيمة الافتراضية وموقع المفتاح الأساسي.
- اكتشاف الفهارس والعروض Views والمشغلات Triggers المضافة أو المحذوفة أو المتغيرة.
- ترتيب ثابت للنتائج لتسهيل المراجعة.
- إخراج نصي أو JSON.
- أمر `inspect` لاستعراض مخطط قاعدة واحدة.
- رموز خروج: `0` للنجاح/التطابق، و`1` لوجود اختلاف، و`2` لخطأ الإدخال أو الفحص.
- Python API بلا اعتماديات تشغيل خارج المكتبة القياسية.
- لا اتصال بالشبكة ولا Telemetry.

### معاينة سريعة
```bash
python examples/create_demo.py
schema-compare compare examples/before.db examples/after.db
```
سيظهر جدول `audit` الجديد وعمود `email` الجديد والفهرس المحذوف.

### المتطلبات والتثبيت
تحتاج Python 3.10 أو أحدث مع دعم SQLite المعتاد في CPython.

```bash
git clone https://github.com/rad03i2/schema-compare.git
cd schema-compare
python -m pip install -e .
```

### الاستخدام
```bash
schema-compare inspect app.db
schema-compare inspect app.db --json
schema-compare compare old.db new.db
schema-compare compare old.db new.db --json
```
رمز الخروج `1` عند الاختلاف مقصود حتى يمكن استخدام الأداة كبوابة داخل CI.

### Python API
```python
from schema_compare import compare_databases

result = compare_databases("old.db", "new.db")
print(result["different"])
```

### الإعداد
لا يوجد ملف إعداد ولا متغيرات بيئة مطلوبة. تمرر مسارات قواعد البيانات صراحة إلى الأداة، ولا توجد مفاتيح أو أسرار أو إعدادات شبكة.

### بنية المشروع
- `src/schema_compare/`: محرك الفحص والمقارنة وواجهة CLI.
- `tests/`: اختبارات تستخدم قواعد SQLite حقيقية مؤقتة.
- `examples/`: مولد مثال قابل لإعادة التشغيل.
- `.github/workflows/`: اختبارات CI متعددة الأنظمة.

### الاختبارات
```bash
python -m pip install -e . pytest
python -m compileall -q src
pytest -q
```
يختبر CI إصدارات Python 3.10 و3.12 و3.13 على Ubuntu وWindows وmacOS.

### الأمان والخصوصية
تُفتح قواعد البيانات بوضع `mode=ro` ولا تنفذ الأداة SQL المخزن في المخطط ولا تعدّل المدخلات، ولا تجري أي اتصال شبكي. مع ذلك قد تكون أسماء الجداول والقيم الافتراضية وتعريفات SQL معلومات حساسة، لذلك يجب حماية التقارير الناتجة. راجع [SECURITY.md](SECURITY.md).

### القيود
- الدعم الحالي لـSQLite فقط.
- لا تتم مقارنة بيانات الصفوف أو تاريخ الترحيلات.
- SQL الخاص بالفهارس والعروض والمشغلات يقارن نصيًا؛ لذلك قد يظهر اختلاف تنسيق مكافئ منطقيًا كاختلاف.
- بعض خصائص SQLite المتقدمة، مثل المقارنة الدلالية الكاملة للمفاتيح الخارجية، ليست ممثلة كفروق مستقلة حاليًا.
- الأداة تكشف الاختلاف ولا تنشئ أو تنفذ migrations.

### تطوير اختياري مستقبلًا
يمكن لاحقًا إضافة تطبيع SQL، وتقارير أعمق للمفاتيح الخارجية، ومحولات لمحركات قواعد بيانات أخرى. هذه أفكار مستقبلية وليست ميزات حالية.

### المساهمة
راجع [CONTRIBUTING.md](CONTRIBUTING.md). يجب أن تتضمن التغييرات السلوكية اختبارات وتحافظ على مبدأ القراءة فقط.

### الترخيص
MIT — راجع [LICENSE](LICENSE).

### المؤلف
**Radwan Abdulhadi Ahmed**  
**رضوان عبدالهادي أحمد**  
GitHub: **@rad03i2**
