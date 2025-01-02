\ProvidesClass{resume}[2024/11/10 v1.0.0 Resume class]
\NeedsTeXFormat{LaTeX2e}
\LoadClassWithOptions{article}

%===============================================================================
% Packages
%===============================================================================
\usepackage[hmargin=0.5in, vmargin=0.25in]{geometry} % Custom margins
\usepackage[no-math]{fontspec}
\usepackage{fontawesome5} % Icons
\usepackage[skip=0pt, indent=0pt]{parskip} % Paragraph skip and indent control
\usepackage[inline]{enumitem} % Itemize environments
\usepackage{etoolbox} % ifstrempty
\usepackage{garamondx} % Garamond font (nonfree)
% \usepackage{ebgaramond} % Garamond font (free)
\usepackage{anyfontsize} % Custom font sizes

\renewcommand{\large}{\fontsize{11}{13}\selectfont}
\renewcommand{\Large}{\fontsize{12}{14.4}\selectfont}
\renewcommand{\LARGE}{\fontsize{16}{19.2}\selectfont}

\newcommand*{\autoleftrightline}[2]{#1\hfill#2}

\newcommand*{\ifEmptyElse}[3]{%
  \ifstrempty{#1}{#2}{#3}%
}

\newcommand*{\subtitle}[3]{%
  \autoleftrightline{{\itshape #1}}{\ifEmptyElse{#3}{#2}{#2---#3}}%
}

\newcommand*{\resumesection}[1]{
  \bigskip%
  {\bfseries\Large #1}\hrulefill%
  \smallskip%
}

% Define an entry of resume information
% Usage: \resumeentry{Title}{Location}{Subtitles}{Description}
\newcommand{\resumeentry}[4]{%
\begin{minipage}{\textwidth}
\large%
\autoleftrightline{{\bfseries #1}}{#2}%
#3%
\normalsize #4%
\end{minipage}
}

\newenvironment*{resumeentryitems}{
    \begin{itemize}[noitemsep, topsep=0pt]
}{
    \end{itemize}
}

\newenvironment*{subtitleitems}{
    \begin{itemize}[noitemsep, topsep=0pt, label={}, leftmargin=0pt]
}{
    \end{itemize}
}

\newcommand*{\headerinfoitem}[2]{\ifEmptyElse{#2}{}{\item #1 #2}}

\newenvironment{header}
  {\begin{tightcenter}\begin{itemize*}[itemjoin=\quad, label={}, afterlabel={}]}
  {\end{itemize*}\end{tightcenter}}

\newenvironment{tightcenter}{
  \setlength\topsep{0pt}
  \setlength\parskip{0pt}
  \setlength\partopsep{0pt}
  \begin{center}
}{
  \end{center}
}