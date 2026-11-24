"""Simulasi lokal alur Multi-Agent dan Fix-Guided Verification Filter."""

from dataclasses import dataclass
from typing import Callable, List, Sequence


@dataclass
class TestCase:
    numbers: List[int]
    expected: List[int]


def filter_even_correct(numbers: Sequence[int]) -> List[int]:
    """Implementasi benar: ambil bilangan genap dan pertahankan urutan."""
    return [number for number in numbers if number % 2 == 0]


def filter_even_buggy(numbers: Sequence[int]) -> List[int]:
    """Implementasi sengaja salah: justru mengambil bilangan ganjil."""
    return [number for number in numbers if number % 2 == 1]


def filter_even_ai_fix(numbers: Sequence[int]) -> List[int]:
    """Contoh kode perbaikan yang diusulkan AI."""
    return [number for number in numbers if number % 2 == 0]


def run_tests(function: Callable[[Sequence[int]], List[int]], cases: List[TestCase]):
    """Jalankan fungsi contoh yang sudah ditulis di file ini pada test cases."""
    results = []
    for index, case in enumerate(cases, start=1):
        try:
            actual = function(case.numbers)
            passed = actual == case.expected
            results.append({
                "test": index,
                "input": case.numbers,
                "expected": case.expected,
                "actual": actual,
                "passed": passed,
            })
        except Exception as exc:  # Menangkap error fungsi contoh agar demo tetap informatif.
            results.append({
                "test": index,
                "input": case.numbers,
                "expected": case.expected,
                "actual": f"ERROR: {type(exc).__name__}: {exc}",
                "passed": False,
            })
    return results


def all_pass(results) -> bool:
    return all(item["passed"] for item in results)


def show_results(label: str, results) -> None:
    print(f"\n{label}")
    print("-" * len(label))
    for item in results:
        status = "PASS" if item["passed"] else "FAIL"
        print(
            f"Test {item['test']}: {status} | "
            f"input={item['input']} | expected={item['expected']} | actual={item['actual']}"
        )


def case_1_false_rejection(cases: List[TestCase]) -> None:
    """Kasus kode asli benar, tetapi AI secara keliru mengusulkan penolakan."""
    print("\n" + "=" * 72)
    print("KASUS 1 — KODE ASLI BENAR, AI SALAH MENOLAK")
    print("=" * 72)

    # Simulasi peran agen. Di tahap ini hasilnya ditulis manual, belum dari API.
    agent_1 = "NO: Agent 1 menduga kode memiliki masalah pada bilangan negatif."
    agent_2 = "YES: Agent 2 menilai dugaan tersebut tidak didukung requirement."
    print("\n[Agent 1 / Reviewer]", agent_1)
    print("[Agent 2 / Critic]  ", agent_2)
    print("\nFilter lalu menguji implementasi asli dan usulan perbaikannya.")

    original_results = run_tests(filter_even_correct, cases)
    fixed_results = run_tests(filter_even_ai_fix, cases)
    show_results("Kode asli", original_results)
    show_results("Kode hasil perbaikan AI", fixed_results)

    original_pass = all_pass(original_results)
    fixed_pass = all_pass(fixed_results)

    # Aturan ilustratif: bila kode asli sudah lulus, jangan pertahankan penolakan
    # hanya karena AI mengusulkan perubahan. Lulus test bukan bukti ekuivalensi mutlak.
    if original_pass and fixed_pass:
        final = "YES — kode asli diterima berdasarkan test suite yang tersedia."
    elif original_pass and not fixed_pass:
        final = "YES — kode asli lulus, sedangkan usulan perbaikan gagal."
    else:
        final = "Perlu evaluasi lanjutan; kode asli tidak lulus seluruh test."

    print("\nKeputusan awal Agent 1: NO")
    print("Keputusan setelah pemeriksaan: ", final)
    print("Catatan: hasil ini hanya berlaku terhadap test case yang dijalankan.")


def case_2_real_bug(cases: List[TestCase]) -> None:
    """Kasus kode asli memang salah dan perbaikan berhasil."""
    print("\n" + "=" * 72)
    print("KASUS 2 — KODE ASLI MEMANG BERCACAT")
    print("=" * 72)

    agent_1 = "NO: Agent 1 menemukan fungsi mengambil bilangan ganjil."
    agent_2 = "NO: Agent 2 mengonfirmasi temuan berdasarkan requirement."
    print("\n[Agent 1 / Reviewer]", agent_1)
    print("[Agent 2 / Critic]  ", agent_2)
    print("\nFilter menguji kode asli dan kode hasil perbaikan.")

    original_results = run_tests(filter_even_buggy, cases)
    fixed_results = run_tests(filter_even_ai_fix, cases)
    show_results("Kode asli yang buggy", original_results)
    show_results("Kode hasil perbaikan AI", fixed_results)

    original_pass = all_pass(original_results)
    fixed_pass = all_pass(fixed_results)

    if not original_pass and fixed_pass:
        final = "NO — penolakan dipertahankan; kode asli gagal dan perbaikannya lulus."
    else:
        final = "Hasil tidak sesuai skenario contoh; perlu diperiksa lagi."

    print("\nKeputusan awal Agent 1: NO")
    print("Keputusan setelah verifikasi:", final)


def run_practice() -> None:
    cases = [
        TestCase(numbers=[1, 2, 3, 4], expected=[2, 4]),
        TestCase(numbers=[], expected=[]),
        TestCase(numbers=[-3, -2, -1, 0, 2], expected=[-2, 0, 2]),
        TestCase(numbers=[5, -4, 7, -6], expected=[-4, -6]),
    ]

    print("=" * 72)
    print("PRAKTIK AWAL: MULTI-AGENT CODE REVIEW + FIX-GUIDED VERIFICATION")
    print("=" * 72)
    print("Requirement: fungsi hanya mengembalikan bilangan genap dan menjaga urutan.")
    print("Mode: simulasi lokal — belum memanggil OpenAI, Gemini, atau Groq API.")

    case_1_false_rejection(cases)
    case_2_real_bug(cases)

    print("\n" + "=" * 72)
    print("SELESAI")
    print("=" * 72)
    print("Yang perlu dipahami:")
    print("1. Agent memberi penilaian berdasarkan requirement.")
    print("2. Agent lain memeriksa atau mengkritisi temuan tersebut.")
    print("3. Filter menjalankan test pada kode asli dan kode usulan perbaikan.")
    print("4. Test yang lulus hanya memberi bukti untuk test suite tersebut,")
    print("   bukan bukti matematis bahwa dua program selalu ekuivalen.")
    print("\nTahap berikutnya: ganti simulasi agen dengan panggilan API sungguhan,")
    print("lalu bangun eksekusi kode yang terisolasi sebelum menguji kode dari PR.")
