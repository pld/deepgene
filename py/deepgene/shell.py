# ABOUTME: Gene research shell interface with lookup command for rsIDs
# ABOUTME: Uses cmd for shell interface and rich for formatted output

import cmd
import dspy
import gnureadline
import os
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from deepgene.gene_lookup import lookup_gene

load_dotenv()
console = Console()


class GeneShell(cmd.Cmd):
    intro = Panel.fit(
        "[bold cyan]DeepGene Research Shell[/bold cyan]\n"
        "Type 'lookup <rsID> <annotation> <positional_gene>' to search for gene information\n"
        "Type 'help' or '?' for commands\n"
        "Type 'exit' or 'quit' to exit",
        border_style="cyan"
    )
    prompt = "\033[1;32mdeepgene>\033[0m "

    def __init__(self):
        super().__init__()
        self.rsid_history = []
        self.setup_dspy()

    def setup_dspy(self):
        """Setup DSPy with Google Gemini 2.5 Flash"""
        console.print("[yellow]Setting up DSPy with Google Gemini 2.5 Flash...[/yellow]")
        try:
            api_key = os.getenv("GOOGLE_API_KEY")
            if not api_key:
                console.print("[red]Error: GOOGLE_API_KEY not found in .env file[/red]")
                console.print("[yellow]Create a .env file with: GOOGLE_API_KEY=your-api-key[/yellow]")
                return

            lm = dspy.LM("gemini/gemini-2.5-flash", api_key=api_key)
            dspy.configure(lm=lm)
            console.print("[green]DSPy configured successfully with Gemini 2.5 Flash[/green]")
        except Exception as e:
            console.print(f"[red]Error setting up DSPy: {e}[/red]")
            console.print("[yellow]Make sure GOOGLE_API_KEY is set in .env file[/yellow]")

    def do_lookup(self, arg):
        """Lookup gene information by rsID. Usage: lookup <rsID> <annotation> <positional_gene>"""
        args = arg.strip().split(maxsplit=2)
        if len(args) < 3:
            console.print("[red]Error: Missing required arguments[/red]")
            console.print("Usage: lookup <rsID> <annotation> <positional_gene>")
            console.print("Example: lookup rs116515942 intronic 'CTNND2 (delta catenin-2)'")
            return

        rsid, annotation, positional_gene = args
        console.print(f"[cyan]Looking up {rsid} ({annotation}, {positional_gene})...[/cyan]")

        try:
            result = self.perform_lookup(rsid, annotation, positional_gene)
            self.display_result(rsid, result)
        except Exception as e:
            console.print(f"[red]Error during lookup: {e}[/red]")

    def complete_lookup(self, text, line, begidx, endidx):
        """Tab completion for lookup command using rsID history"""
        if not text:
            return self.rsid_history
        return [rsid for rsid in self.rsid_history if rsid.startswith(text)]

    def perform_lookup(self, rsid, annotation, positional_gene):
        """Use DSPy to lookup gene information with database enrichment"""
        from deepgene.gene_parser import extract_gene_symbol
        from deepgene.gene_data import fetch_gene_data

        if rsid not in self.rsid_history:
            self.rsid_history.append(rsid)

        gene_symbol = extract_gene_symbol(positional_gene)
        gene_data = None

        if gene_symbol:
            console.print(f"[dim]Fetching {gene_symbol} from MyGene.info...[/dim]")
            try:
                gene_data = fetch_gene_data(gene_symbol)
                if gene_data:
                    console.print("[dim green]✓ Database data retrieved[/dim green]")
                else:
                    console.print("[dim yellow]⚠ No data found, AI-only mode[/dim yellow]")
            except Exception as e:
                console.print(f"[dim yellow]⚠ Database error, AI-only mode[/dim yellow]")

        with console.status("[cyan]Analyzing with Gemini...[/cyan]", spinner="dots"):
            result = lookup_gene(rsid, annotation, positional_gene, gene_data)

        return result

    def display_result(self, rsid, result):
        """Display gene lookup results as a research report"""
        from rich.panel import Panel
        from rich.text import Text

        console.print()
        console.print(Panel.fit(
            f"[bold cyan]Gene Research Report: {rsid}[/bold cyan]",
            border_style="cyan"
        ))
        console.print()

        console.print(f"[bold cyan]Annotation:[/bold cyan] {result.get('annotation', 'N/A')}")
        console.print(f"[bold cyan]Positional Gene:[/bold cyan] {result.get('positional_gene', 'N/A')}")
        console.print()

        gene_data = result.get('gene_data')
        if gene_data:
            console.print("[bold green]Gene Database Information[/bold green] [dim](MyGene.info)[/dim]")
            console.print()

            if gene_data.gene_name:
                console.print(f"  [cyan]Gene:[/cyan] {gene_data.gene_symbol} - {gene_data.gene_name}")

            if gene_data.summary:
                summary_text = gene_data.summary[:200] + "..." if len(gene_data.summary) > 200 else gene_data.summary
                console.print(f"  [cyan]Summary:[/cyan] {summary_text}")

            if gene_data.pathways:
                console.print(f"  [cyan]Pathways:[/cyan]")
                for pathway in gene_data.pathways[:5]:
                    console.print(f"    • {pathway}")

            if gene_data.mim_diseases:
                console.print(f"  [cyan]OMIM Diseases:[/cyan]")
                for disease in gene_data.mim_diseases[:3]:
                    console.print(f"    • {disease}")

            if gene_data.genomic_location:
                console.print(f"  [cyan]Location:[/cyan] {gene_data.genomic_location}")

            console.print()

        console.print("[bold yellow]Function[/bold yellow] [dim](AI Analysis)[/dim]")
        functions = result.get('function', [])
        if isinstance(functions, list) and functions:
            for func in functions:
                console.print(f"  • {func}")
        else:
            console.print(f"  {functions}")
        console.print()

        console.print("[bold yellow]Associated Diseases[/bold yellow] [dim](AI Analysis)[/dim]")
        diseases = result.get('diseases', [])
        if isinstance(diseases, list) and diseases:
            for disease in diseases:
                console.print(f"  • {disease}")
        else:
            console.print(f"  {diseases}")
        console.print()

        console.print("[bold yellow]Associated SNPs[/bold yellow] [dim](AI Analysis)[/dim]")
        snps = result.get('snps', {})
        if isinstance(snps, dict) and snps:
            for snp_id, snp_info in snps.items():
                console.print(f"  [cyan]{snp_id}[/cyan]")
                if hasattr(snp_info, 'genes'):
                    console.print(f"    Genes: {', '.join(snp_info.genes)}")
                if hasattr(snp_info, 'phenotypes'):
                    console.print(f"    Phenotypes: {', '.join(snp_info.phenotypes)}")
        else:
            console.print("  None")
        console.print()

        console.print("[bold yellow]Literature & References[/bold yellow] [dim](AI + NER Analysis)[/dim]")
        literature = result.get('literature', [])
        if isinstance(literature, list) and literature:
            for idx, lit in enumerate(literature, 1):
                if hasattr(lit, 'functional_relevance'):
                    console.print(f"  [bold cyan][{idx}][/bold cyan] {lit.functional_relevance}")
                    if hasattr(lit, 'mutants') and lit.mutants:
                        mutant_count = len(lit.mutants)
                        mutant_display = ', '.join(lit.mutants[:10])
                        console.print(f"      [dim]Mutants ({mutant_count} found): {mutant_display}[/dim]")
                        if mutant_count > 10:
                            console.print(f"      [dim]... and {mutant_count - 10} more[/dim]")
                    if hasattr(lit, 'url'):
                        console.print(f"      [link={lit.url}]{lit.url}[/link]")
                    console.print()
        else:
            console.print("  None")
        console.print()

    def do_exit(self, arg):
        """Exit the shell"""
        console.print("[yellow]Goodbye![/yellow]")
        return True

    def do_quit(self, arg):
        """Exit the shell"""
        return self.do_exit(arg)

    def do_EOF(self, arg):
        """Exit on Ctrl+D"""
        console.print()
        return self.do_exit(arg)

    def cmdloop(self, intro=None):
        """Override cmdloop to use rich for intro"""
        if intro is not None:
            self.intro = intro
        if self.intro:
            console.print(self.intro)
        super().cmdloop(intro="")


def main():
    """Entry point for the gene shell"""
    shell = GeneShell()
    shell.cmdloop()


if __name__ == "__main__":
    main()
