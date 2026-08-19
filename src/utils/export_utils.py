"""
Export utilities for Personal Expense Tracker.

This module provides functions to export expense data to CSV and PDF formats.
"""

import csv
import io
from datetime import datetime
from typing import List, Dict, Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT


def generate_csv(expenses: List[Dict[str, Any]]) -> str:
    """
    Generate CSV content from expenses data.
    
    Args:
        expenses: List of expense dictionaries
        
    Returns:
        CSV content as string
    """
    output = io.StringIO()
    
    if not expenses:
        return ""
    
    # Define CSV headers
    fieldnames = ['Date', 'Business', 'Amount', 'Category', 'Description']
    
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    
    for expense in expenses:
        writer.writerow({
            'Date': expense.get('date', ''),
            'Business': expense.get('business', ''),
            'Amount': f"{expense.get('amount', 0):.2f}",
            'Category': expense.get('category', ''),
            'Description': expense.get('description', '')
        })
    
    return output.getvalue()


def generate_pdf(expenses: List[Dict[str, Any]], 
                 title: str = "Expense Report",
                 date_range: str = None) -> bytes:
    """
    Generate PDF report from expenses data.
    
    Args:
        expenses: List of expense dictionaries
        title: Report title
        date_range: Optional date range string to display
        
    Returns:
        PDF content as bytes
    """
    buffer = io.BytesIO()
    
    # Create PDF document
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=0.5*inch,
        leftMargin=0.5*inch,
        topMargin=0.75*inch,
        bottomMargin=0.5*inch
    )
    
    # Container for PDF elements
    elements = []
    
    # Define styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#4e7aa6'),
        spaceAfter=12,
        alignment=TA_CENTER
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Normal'],
        fontSize=12,
        textColor=colors.grey,
        spaceAfter=20,
        alignment=TA_CENTER
    )
    
    # Add title
    title_para = Paragraph(title, title_style)
    elements.append(title_para)
    
    # Add date range if provided
    if date_range:
        date_para = Paragraph(f"Period: {date_range}", subtitle_style)
        elements.append(date_para)
    
    # Add generation date
    gen_date = datetime.now().strftime("%B %d, %Y at %I:%M %p")
    gen_para = Paragraph(f"Generated on: {gen_date}", subtitle_style)
    elements.append(gen_para)
    
    elements.append(Spacer(1, 0.2*inch))
    
    if not expenses:
        no_data_para = Paragraph("No expenses found for the selected period.", styles['Normal'])
        elements.append(no_data_para)
    else:
        # Calculate summary statistics
        total_amount = sum(exp.get('amount', 0) for exp in expenses)
        avg_amount = total_amount / len(expenses) if expenses else 0
        
        # Add summary section
        summary_data = [
            ['Total Expenses:', f'${total_amount:,.2f}'],
            ['Number of Transactions:', str(len(expenses))],
            ['Average Amount:', f'${avg_amount:,.2f}']
        ]
        
        summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e0e0e0')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey)
        ]))
        
        elements.append(summary_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Add detailed expenses table
        detail_title = Paragraph("Detailed Expenses", styles['Heading2'])
        elements.append(detail_title)
        elements.append(Spacer(1, 0.1*inch))
        
        # Prepare table data
        table_data = [['Date', 'Business', 'Amount', 'Category', 'Description']]
        
        for expense in expenses:
            table_data.append([
                expense.get('date', ''),
                expense.get('business', '')[:30],  # Truncate long business names
                f"${expense.get('amount', 0):.2f}",
                expense.get('category', ''),
                (expense.get('description', '') or '')[:40]  # Truncate long descriptions
            ])
        
        # Create table
        col_widths = [1*inch, 2*inch, 1*inch, 1.5*inch, 2*inch]
        expense_table = Table(table_data, colWidths=col_widths, repeatRows=1)
        
        # Style the table
        table_style = TableStyle([
            # Header row
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4e7aa6')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            
            # Data rows
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),  # Date
            ('ALIGN', (1, 1), (1, -1), 'LEFT'),  # Business
            ('ALIGN', (2, 1), (2, -1), 'RIGHT'),  # Amount
            ('ALIGN', (3, 1), (3, -1), 'LEFT'),  # Category
            ('ALIGN', (4, 1), (4, -1), 'LEFT'),  # Description
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('TOPPADDING', (0, 1), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 5),
            
            # Alternating row colors
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f0f0')]),
            
            # Grid
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
        ])
        
        expense_table.setStyle(table_style)
        elements.append(expense_table)
    
    # Build PDF
    doc.build(elements)
    
    # Get PDF content
    pdf_content = buffer.getvalue()
    buffer.close()
    
    return pdf_content


def generate_category_summary_csv(category_data: List[Dict[str, Any]]) -> str:
    """
    Generate CSV for category-wise summary.
    
    Args:
        category_data: List of category summary dictionaries
        
    Returns:
        CSV content as string
    """
    output = io.StringIO()
    
    if not category_data:
        return ""
    
    fieldnames = ['Category', 'Total Amount', 'Percentage']
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    
    total = sum(cat.get('category_amount', 0) for cat in category_data)
    
    for cat in category_data:
        amount = cat.get('category_amount', 0)
        percentage = (amount / total * 100) if total > 0 else 0
        
        writer.writerow({
            'Category': cat.get('category', ''),
            'Total Amount': f"{amount:.2f}",
            'Percentage': f"{percentage:.1f}%"
        })
    
    # Add total row
    writer.writerow({
        'Category': 'TOTAL',
        'Total Amount': f"{total:.2f}",
        'Percentage': '100.0%'
    })
    
    return output.getvalue()
