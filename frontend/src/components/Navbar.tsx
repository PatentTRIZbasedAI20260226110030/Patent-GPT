"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Button } from "@/components/ui/button";

export function Navbar() {
  const pathname = usePathname();

  return (
    <nav className="flex items-center justify-between px-4 sm:px-6 py-3 sm:py-4 max-w-content mx-auto w-full">
      <Link
        href="/"
        className="text-lg sm:text-xl font-bold text-text-primary whitespace-nowrap"
      >
        Patent-GPT
      </Link>
      <div className="flex gap-2 sm:gap-3">
        <Link href="/search">
          <Button
            variant={pathname === "/search" ? "primary" : "ghost"}
            size="sm"
            className="text-xs sm:text-sm sm:h-11 sm:px-6"
          >
            <span className="sm:hidden">검색</span>
            <span className="hidden sm:inline">선행특허 검색</span>
          </Button>
        </Link>
        <Link href="/generate">
          <Button
            variant={pathname === "/generate" ? "primary" : "ghost"}
            size="sm"
            className="text-xs sm:text-sm sm:h-11 sm:px-6"
          >
            <span className="sm:hidden">생성</span>
            <span className="hidden sm:inline">특허 생성하기</span>
          </Button>
        </Link>
      </div>
    </nav>
  );
}
