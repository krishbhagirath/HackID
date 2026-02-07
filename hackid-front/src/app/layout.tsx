import "~/styles/globals.css";

import { type Metadata } from "next";
import { Syne, Space_Mono } from "next/font/google";

const syne = Syne({
  subsets: ["latin"],
  weight: ["800"],
  variable: "--font-syne",
});

const spaceMono = Space_Mono({
  subsets: ["latin"],
  weight: ["400", "700"],
  variable: "--font-space-mono",
});

export const metadata: Metadata = {
  title: "HackCheck // Submission Validator",
  description: "Plagiarism Detection Engine for Hackathons",
  icons: [{ rel: "icon", url: "/favicon.ico" }],
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en" className={`${syne.variable} ${spaceMono.variable} dark`}>
       <head>
        <link
          href="https://fonts.googleapis.com/icon?family=Material+Icons"
          rel="stylesheet"
        />
      </head>
      <body className="bg-background-light dark:bg-background-dark text-white dark:text-white transition-colors duration-200">
        {children}
      </body>
    </html>
  );
}
