%! Package = PyRollDocs
%! Author = Max Weiner
%! Date = 11.02.22

\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{PyRollDocs}[2022/02/22 Class for documentation of PyRoll]

\DeclareOption*{\PassOptionsToClass{\CurrentOption}{scrartcl}}
\ProcessOptions\relax
\LoadClass{scrartcl}

\RequirePackage[automark,headsepline]{scrlayer-scrpage}
\clearpairofpagestyles

\makeatletter

\ifoot*{\@author\ -- \@date}
\ofoot*{\pagemark}
\ihead{\@title}
\ohead{\headmark}

\makeatother

\pagestyle{scrheadings}

\RequirePackage[utf8]{inputenc}
\RequirePackage[T1]{fontenc}

% Packages
\RequirePackage{amsmath}
\RequirePackage[backend=biber, maxcitenames=99, sorting=none]{biblatex}
\RequirePackage{booktabs}
\RequirePackage{graphicx}
\RequirePackage{siunitx}
\RequirePackage{subcaption}
\RequirePackage[hidelinks]{hyperref}

\RequirePackage{xcolor}
\RequirePackage{minted}
\setminted{autogobble}

\providecommand{\abs}[1]{\lvert#1\rvert}