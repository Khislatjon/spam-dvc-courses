# SPAM DVC Courses

Two free, hands-on courses on digital volume correlation (DVC) with [SPAM](https://ttk.gricad-pages.univ-grenoble-alpes.fr/spam/).

| Course | Lessons | Time | What you learn |
|---|---|---|---|
| 1. How SPAM DVC Works | 8 | About 90 minutes | The ideas, from a squeezed block of jelly to a full displacement field |
| 2. SPAM Commands | 7 | About 75 minutes | Every key command-line flag, using real SPAM runs on a test sample with a known answer |

Each lesson has an explainer character, Vox, interactive labs, and notes linking each idea to SPAM's own code.

## Open the courses

Online: <https://khislatjon.github.io/spam-dvc-courses/>

Offline: open `START HERE.html` in a web browser. Everything works offline, apart from the web fonts.

## Rebuild after editing

The lesson sources are in `source/`. After editing them, run:

```bash
bash source/build_all.sh
```

| Folder | Contents |
|---|---|
| `source/course1` | Builder, shared lab code, lessons and the two videos for Course 1 |
| `source/course2` | Builder, lessons, and the experiment scripts and results behind Course 2 |
| `source/home` | The home page builder |

`source/course2/exp/experiments.py` and `exp2.py` make the test sample and rerun the SPAM experiments. They need SPAM, NumPy, SciPy, pandas and tifffile. The results are already saved as JSON, so you don't need to rerun them to rebuild the courses.

## Credits

SPAM (Software for Practical Analysis of Materials) is open-source software by its own developers. If you use it, please cite Stamati et al., *spam: Software for Practical Analysis of Materials*, Journal of Open Source Software, 2020. These courses are independent, and are not made by or endorsed by the SPAM team. They were written using SPAM 0.8.1.4.
